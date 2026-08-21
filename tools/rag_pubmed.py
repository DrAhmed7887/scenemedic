"""BigQuery Vector Search over the SceneMedic clinical corpus."""
from __future__ import annotations

import os

from google.cloud import bigquery
from vertexai.language_models import TextEmbeddingModel

_bq = bigquery.Client()
_embed = TextEmbeddingModel.from_pretrained("text-embedding-004")

_DATASET = os.getenv("BQ_CORPUS_DATASET", "scenemedic")
_TABLE = os.getenv("BQ_CORPUS_TABLE", "pubmed_chunks")


def search_pubmed(query: str, k: int = 5) -> list[dict]:
    """Semantic search over the clinical corpus. Returns list of
    {title, snippet, url, score}."""
    vec = _embed.get_embeddings([query])[0].values
    sql = f"""
    SELECT title, snippet, url,
           1 - ML.DISTANCE(embedding, @qvec, 'COSINE') AS score
    FROM `{_DATASET}.{_TABLE}`
    ORDER BY ML.DISTANCE(embedding, @qvec, 'COSINE')
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
