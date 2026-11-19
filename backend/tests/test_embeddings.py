import numpy as np
from backend.app.services.embedding_service import EmbeddingService

def test_embed_single_text():
    service = EmbeddingService()
    emb = service.embed_text("Artificial Intelligence and Knowledge Graphs")
    assert isinstance(emb, np.ndarray)
    assert emb.shape == (384,)
    # Verify unit norm (L2 normalization)
    norm = np.linalg.norm(emb)
    assert abs(norm - 1.0) < 1e-4

def test_embed_batch():
    service = EmbeddingService()
    texts = [
        "First document text chunk for embedding.",
        "Second document text chunk with different semantic meaning."
    ]
    embs = service.embed_batch(texts)
    assert embs.shape == (2, 384)
    # Cosine similarity between normalized vectors is dot product
    sim = np.dot(embs[0], embs[1])
    assert -1.0 <= sim <= 1.0

