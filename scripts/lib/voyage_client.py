"""Voyage AI embedding client extracted from build_index.py."""

import time

import requests

VOYAGE_API_URL = "https://api.voyageai.com/v1/embeddings"
EMBEDDING_MODEL = "voyage-3"
EMBEDDING_BATCH_SIZE = 128  # Voyage supports up to 128 per batch


def generate_embeddings(
    texts: list[str],
    api_key: str,
    input_type: str = "document",
) -> list[list[float]]:
    """Generate embeddings for a list of texts using Voyage AI API."""
    all_embeddings: list[list[float]] = [[] for _ in texts]

    for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[i : i + EMBEDDING_BATCH_SIZE]
        print(f"  Generating embeddings batch {i // EMBEDDING_BATCH_SIZE + 1} ({len(batch)} texts)...")

        resp = requests.post(
            VOYAGE_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": EMBEDDING_MODEL,
                "input": batch,
                "input_type": input_type,
            },
        )
        resp.raise_for_status()
        data = resp.json()

        for j, item in enumerate(data["data"]):
            all_embeddings[i + j] = item["embedding"]

        # Respect rate limits
        if i + EMBEDDING_BATCH_SIZE < len(texts):
            time.sleep(0.5)

    return all_embeddings
