import numpy as np
from backend.app.services.vector_store import VectorStore

def test_vector_store_add_and_search(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.app.core.config.settings.VECTOR_DIR", str(tmp_path))
    vs = VectorStore()
    vs.reset_index()

    # Generate dummy normalized embeddings
    v1 = np.random.randn(384).astype(np.float32)
    v1 /= np.linalg.norm(v1)
    v2 = np.random.randn(384).astype(np.float32)
    v2 /= np.linalg.norm(v2)

    embeddings = np.stack([v1, v2])
    chunk_ids = ["chunk-alpha", "chunk-beta"]

    faiss_ids = vs.add_embeddings(chunk_ids, embeddings)
    assert len(faiss_ids) == 2
    assert vs.index.ntotal == 2

    # Query with exact v1 vector
    results = vs.search(v1, top_k=2)
    assert len(results) == 2
    assert results[0][0] == "chunk-alpha"
    assert abs(results[0][1] - 1.0) < 1e-4

    # Test filtering
    filtered_results = vs.search(v1, top_k=2, allowed_chunk_ids={"chunk-beta"})
    assert len(filtered_results) == 1
    assert filtered_results[0][0] == "chunk-beta"

    # Test removal
    vs.remove_chunks(["chunk-alpha"])
    assert vs.index.ntotal == 1
    remaining_results = vs.search(v1, top_k=2)
    assert len(remaining_results) == 1
    assert remaining_results[0][0] == "chunk-beta"

