"""BigQuery Vector Search over the SceneMedic clinical corpus.

Embeddings via google-genai (AI Studio) — no Vertex client needed, so this
runs on the free tier while the hackathon Vertex credit is pending.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai
from google.cloud import bigquery

load_dotenv()

_bq = bigquery.Client()
_gen = genai.Client()

_DATASET = os.getenv("BQ_CORPUS_DATASET", "scenemedic")
_TABLE = os.getenv("BQ_CORPUS_TABLE", "pubmed_chunks")
_MODEL = os.getenv("EMBED_MODEL", "gemini-embedding-001")


def search_pubmed(query: str, k: int = 5) -> list[dict]:
    """Semantic search over the clinical corpus.

    Returns a list of {title, snippet, url, score}, best-first.
    """
    vec = list(_gen.models.embed_content(model=_MODEL, contents=query)
               .embeddings[0].values)
    sql = f"""
    SELECT
      title, snippet, url,
      (
        SELECT SUM(a*b) / (SQRT(SUM(a*a)) * SQRT(SUM(b*b)))
        FROM UNNEST(embedding) a WITH OFFSET p
        JOIN UNNEST(@qvec) b WITH OFFSET q ON p = q
      ) AS score
    FROM `{_bq.project}.{_DATASET}.{_TABLE}`
    ORDER BY score DESC
    LIMIT @k
    """
    job = _bq.query(
        sql,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("qvec", "FLOAT64", vec),
                bigquery.ScalarQueryParameter("k", "INT64", k),
            ]
        ),
    )
    return [dict(r) for r in job.result()]
