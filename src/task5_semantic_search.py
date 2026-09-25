"""Dense search using Task 4's shared encoder and cosine collection."""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Return unique results sorted by raw cosine similarity."""
    if not query.strip() or top_k <= 0:
        return []
    response = get_collection().query(
        query_embeddings=embed_texts([query]), n_results=top_k,
        include=['documents', 'metadatas', 'distances'],
    )
    results = {}
    for item_id, content, metadata, distance in zip(
        response['ids'][0], response['documents'][0],
        response['metadatas'][0], response['distances'][0],
    ):
        metadata = dict(metadata)
        metadata['url'] = metadata.get('url') or None
        item = {
            'id': item_id, 'content': content, 'metadata': metadata,
            'score': float(1.0 - distance), 'retrieval_method': 'dense',
        }
        if item_id not in results or item['score'] > results[item_id]['score']:
            results[item_id] = item
    return sorted(results.values(), key=lambda item: item['score'], reverse=True)[:top_k]
