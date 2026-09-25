"""Recursive Markdown chunking and persistent cosine indexing with local BGE."""

from functools import lru_cache
import math
from pathlib import Path
import re

from src.contracts import validate_document

STANDARDIZED_DIR = Path(__file__).resolve().parent.parent / 'data' / 'standardized'
CHROMA_DIR = Path(__file__).resolve().parent.parent / 'chroma_db'
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = 'recursive'
EMBEDDING_MODEL = 'BAAI/bge-m3'
EMBEDDING_DIM = 1024
EMBEDDING_BATCH_SIZE = 32
INDEX_BATCH_SIZE = 128
COLLECTION_NAME = 'rag_documents'


@lru_cache(maxsize=1)
def _get_embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def _validate_vectors(vectors, count):
    if len(vectors) != count:
        raise ValueError('Embedding count does not match text count')
    for vector in vectors:
        if len(vector) != EMBEDDING_DIM:
            raise ValueError(f'Expected embedding dimension {EMBEDDING_DIM}')
        if not all(math.isfinite(value) for value in vector) or not any(vector):
            raise ValueError('Embeddings must be finite and non-zero')


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Shared encoder for documents and queries; no provider fallback."""
    if not texts:
        return []
    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError('Embedding texts must be non-empty strings')
    vectors = _get_embedding_model().encode(
        texts, batch_size=EMBEDDING_BATCH_SIZE, normalize_embeddings=True,
        convert_to_numpy=True, show_progress_bar=False,
    ).tolist()
    _validate_vectors(vectors, len(texts))
    return vectors


def get_collection():
    """Open a cosine collection without an implicit embedding provider."""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    expected = {'hnsw:space': 'cosine', 'embedding_model': EMBEDDING_MODEL,
                'embedding_dim': EMBEDDING_DIM}
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, metadata=expected, embedding_function=None,
    )
    if any((collection.metadata or {}).get(k) != v for k, v in expected.items()):
        raise ValueError('Incompatible collection metric/model/dimension; use a new collection')
    return collection


def load_documents() -> list[dict]:
    """Read all Markdown files and retain Task 3 titles and source URLs."""
    if not STANDARDIZED_DIR.is_dir():
        raise FileNotFoundError(f'Missing directory: {STANDARDIZED_DIR}')
    documents = []
    for path in sorted(STANDARDIZED_DIR.rglob('*')):
        if not path.is_file() or path.suffix.lower() != '.md':
            continue
        content = path.read_text(encoding='utf-8-sig').strip()
        if not content:
            continue
        relative = path.relative_to(STANDARDIZED_DIR)
        heading = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        url = re.search(r'^\*\*Source:\*\*\s*(https?://\S+)', content, re.MULTILINE)
        document = {
            'id': relative.as_posix(), 'content': content,
            'metadata': {
                'source': relative.as_posix(),
                'title': heading.group(1).strip() if heading else content.splitlines()[0],
                'doc_type': 'legal' if 'legal' in relative.parts[:-1] else 'news',
                'url': url.group(1) if url else None,
            },
        }
        validate_document(document)
        documents.append(document)
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Split by characters with stable document ID / chunk position IDs."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    if CHUNKING_METHOD != 'recursive':
        raise ValueError(f'Unsupported chunking method: {CHUNKING_METHOD}')
    if not 0 <= CHUNK_OVERLAP < CHUNK_SIZE:
        raise ValueError('Require 0 <= CHUNK_OVERLAP < CHUNK_SIZE')
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
        separators=['\n\n', '\n', '. ', ' ', ''],
    )
    chunks = []
    seen = set()
    for document in documents:
        validate_document(document)
        if document['id'] in seen:
            raise ValueError('Document IDs must be unique')
        seen.add(document['id'])
        for index, text in enumerate(splitter.split_text(document['content'])):
            chunk = {
                'id': f"{document['id']}::chunk-{index}", 'content': text,
                'metadata': {**document['metadata'], 'chunk_index': index},
            }
            validate_document(chunk, require_chunk=True)
            chunks.append(chunk)
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Embed bounded batches without mutating input chunks."""
    for chunk in chunks:
        validate_document(chunk, require_chunk=True)
    embedded = []
    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[start:start + EMBEDDING_BATCH_SIZE]
        vectors = embed_texts([chunk['content'] for chunk in batch])
        _validate_vectors(vectors, len(batch))
        embedded.extend({**chunk, 'metadata': dict(chunk['metadata']), 'embedding': vector}
                        for chunk, vector in zip(batch, vectors))
    return embedded


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert stable IDs, making repeated indexing of identical input idempotent."""
    if not chunks:
        return
    for chunk in chunks:
        validate_document(chunk, require_chunk=True)
    if len({chunk['id'] for chunk in chunks}) != len(chunks):
        raise ValueError('Chunk IDs must be unique')
    _validate_vectors([chunk['embedding'] for chunk in chunks], len(chunks))
    collection = get_collection()
    for start in range(0, len(chunks), INDEX_BATCH_SIZE):
        batch = chunks[start:start + INDEX_BATCH_SIZE]
        collection.upsert(
            ids=[chunk['id'] for chunk in batch],
            documents=[chunk['content'] for chunk in batch],
            embeddings=[chunk['embedding'] for chunk in batch],
            # Chroma does not accept None metadata; Task 5 restores nullable URLs.
            metadatas=[{k: '' if v is None else v for k, v in chunk['metadata'].items()}
                       for chunk in batch],
        )


def run_pipeline() -> None:
    documents = load_documents()
    chunks = chunk_documents(documents)
    index_to_vectorstore(embed_chunks(chunks))
    print(f'Indexed {len(chunks)} chunks from {len(documents)} documents')


if __name__ == '__main__':
    run_pipeline()
