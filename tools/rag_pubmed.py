"""BigQuery Vector Search over the SceneMedic clinical corpus.

Embeddings via google-genai on Vertex (explicit vertexai=True), so it works
inside the Agent Engine runtime without leaking to AI Studio when
GEMINI_API_KEY happens to be present in local dev shells.

Clients are constructed lazily so this module imports cleanly even when
GOOGLE_CLOUD_PROJECT isn't set (e.g. dry-run tool-schema introspection).
"""
from __future__ import annotations

import os

from google import genai
from google.cloud import bigquery

_DATASET = os.getenv("BQ_CORPUS_DATASET", "scenemedic")
_TABLE = os.getenv("BQ_CORPUS_TABLE", "pubmed_chunks")
_MODEL = os.getenv("EMBED_MODEL", "gemini-embedding-001")

_bq: bigquery.Client | None = None
_gen: genai.Client | None = None


def _bq_client() -> bigquery.Client:
    global _bq
    if _bq is None:
        _bq = bigquery.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"])
    return _bq


def _gen_client() -> genai.Client:
    global _gen
    if _gen is None:
        _gen = genai.Client(
            vertexai=True,
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    return _gen


def search_pubmed(query: str, k: int = 5) -> list[dict]:
    """Semantic search over the clinical corpus.

    Returns a list of {title, snippet, url, score}, best-first.
    """
    gen = _gen_client()
    bq = _bq_client()
    vec = list(gen.models.embed_content(model=_MODEL, contents=query)
               .embeddings[0].values)
    sql = f"""
    SELECT
      title, snippet, url,
      (
        SELECT SUM(a*b) / (SQRT(SUM(a*a)) * SQRT(SUM(b*b)))
        FROM UNNEST(embedding) a WITH OFFSET p
        JOIN UNNEST(@qvec) b WITH OFFSET q ON p = q
      ) AS score
    FROM `{bq.project}.{_DATASET}.{_TABLE}`
    ORDER BY score DESC
    LIMIT @k
    """
    job = bq.query(
        sql,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("qvec", "FLOAT64", vec),
                bigquery.ScalarQueryParameter("k", "INT64", k),
            ]
        ),
    )
    return [dict(r) for r in job.result()]
