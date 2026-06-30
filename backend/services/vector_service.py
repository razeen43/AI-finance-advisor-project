import faiss
import numpy as np
from services.embedding_service import embed_text

DIMENSION = 384

index = faiss.IndexFlatL2(DIMENSION)
metadata = []


def clear_index():
    global index, metadata
    index = faiss.IndexFlatL2(DIMENSION)
    metadata = []


def add_transaction_to_index(transaction):
    text = f"{transaction.get('merchant', '')} {transaction.get('category', '')} {transaction.get('amount', '')}"

    vector = embed_text(text)
    vector_np = np.array([vector]).astype("float32")

    index.add(vector_np)
    metadata.append(transaction)


def search_transactions(query, user_id, top_k=5):
    if index.ntotal == 0:
        return []

    query_vector = embed_text(query)
    query_np = np.array([query_vector]).astype("float32")

    k = min(top_k * 5, index.ntotal)

    distances, indexes = index.search(query_np, k)

    results = []

    for idx in indexes[0]:
        if idx != -1 and idx < len(metadata):
            transaction = metadata[idx]

            if transaction.get("user_id") == user_id:
                results.append(transaction)

            if len(results) >= top_k:
                break

    return results