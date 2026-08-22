"""Seed the BigQuery Vector Search corpus.

Usage:
  python corpus/ingest_pubmed.py --input corpus/seed.jsonl

Expects JSONL rows: {"title": str, "snippet": str, "url": str}.
Embeddings via google-genai (AI Studio free tier) — no Vertex needed.
"""
from __future__ import annotations

import argparse
import json
import os

from dotenv import load_dotenv
from google import genai
from google.cloud import bigquery

load_dotenv()

_bq = bigquery.Client()
_gen = genai.Client()

DATASET = os.getenv("BQ_CORPUS_DATASET", "scenemedic")
TABLE = os.getenv("BQ_CORPUS_TABLE", "pubmed_chunks")
EMBED_MODEL = os.getenv("EMBED_MODEL", "gemini-embedding-001")
EMBED_DIM = 3072


def ensure_table() -> None:
    ds = bigquery.Dataset(f"{_bq.project}.{DATASET}")
    ds.location = os.getenv("GOOGLE_CLOUD_LOCATION", "US")
    _bq.create_dataset(ds, exists_ok=True)
    schema = [
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("snippet", "STRING"),
        bigquery.SchemaField("url", "STRING"),
        bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
    ]
    table = bigquery.Table(f"{_bq.project}.{DATASET}.{TABLE}", schema=schema)
    _bq.create_table(table, exists_ok=True)


def embed(text: str) -> list[float]:
    r = _gen.models.embed_content(model=EMBED_MODEL, contents=text)
    return list(r.embeddings[0].values)


def load(path: str) -> None:
    ensure_table()
    rows: list[dict] = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            r = json.loads(line)
            r["embedding"] = embed(r["snippet"])
            rows.append(r)
            if i % 10 == 0:
                print(f"  embedded {i}...")
    errors = _bq.insert_rows_json(f"{DATASET}.{TABLE}", rows)
    if errors:
        raise RuntimeError(errors)
    print(f"Inserted {len(rows)} chunks into {_bq.project}.{DATASET}.{TABLE}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    load(ap.parse_args().input)
