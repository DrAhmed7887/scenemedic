"""Seed the BigQuery Vector Search corpus.

Usage:
  python corpus/ingest_pubmed.py --input corpus/seed.jsonl

Expects JSONL rows: {"title": str, "snippet": str, "url": str}.
"""
from __future__ import annotations

import argparse
import json
import os

from google.cloud import bigquery
from vertexai.language_models import TextEmbeddingModel

_bq = bigquery.Client()
_embed = TextEmbeddingModel.from_pretrained("text-embedding-004")

DATASET = os.getenv("BQ_CORPUS_DATASET", "scenemedic")
TABLE = os.getenv("BQ_CORPUS_TABLE", "pubmed_chunks")


def ensure_table() -> None:
    ds = bigquery.Dataset(f"{_bq.project}.{DATASET}")
    _bq.create_dataset(ds, exists_ok=True)
    schema = [
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("snippet", "STRING"),
        bigquery.SchemaField("url", "STRING"),
        bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
    ]
    table = bigquery.Table(f"{_bq.project}.{DATASET}.{TABLE}", schema=schema)
    _bq.create_table(table, exists_ok=True)


def load(path: str) -> None:
    ensure_table()
    rows: list[dict] = []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            vec = _embed.get_embeddings([r["snippet"]])[0].values
            rows.append({**r, "embedding": list(vec)})
    errors = _bq.insert_rows_json(f"{DATASET}.{TABLE}", rows)
    if errors:
        raise RuntimeError(errors)
    print(f"Inserted {len(rows)} chunks.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    load(ap.parse_args().input)
