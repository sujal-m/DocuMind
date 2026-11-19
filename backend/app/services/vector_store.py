import os
import json
import threading
from typing import List, Dict, Tuple, Optional
import numpy as np
import faiss
from backend.app.core.config import settings
from backend.app.core.logging import logger

class VectorStore:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VectorStore, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.dimension = settings.EMBEDDING_DIMENSION
        self.index_dir = settings.VECTOR_DIR
        self.index_file = os.path.join(self.index_dir, "index.faiss")
        self.metadata_file = os.path.join(self.index_dir, "index_metadata.json")

        # Map faiss_id (int) -> chunk_id (str)
        self.faiss_to_chunk: Dict[int, str] = {}
        # Map chunk_id (str) -> faiss_id (int)
        self.chunk_to_faiss: Dict[str, int] = {}
        self.next_faiss_id: int = 1

        self._load_or_create_index()
        self._initialized = True

    def _load_or_create_index(self):
        """Loads FAISS index and mapping from disk if present, else creates new."""
        os.makedirs(self.index_dir, exist_ok=True)

        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            try:
                logger.info(f"Loading FAISS index from {self.index_file}...")
                self.index = faiss.read_index(self.index_file)
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.faiss_to_chunk = {int(k): v for k, v in meta.get("faiss_to_chunk", {}).items()}
                    self.chunk_to_faiss = meta.get("chunk_to_faiss", {})
                    self.next_faiss_id = meta.get("next_faiss_id", 1)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors.")
                return
            except Exception as e:
                logger.error(f"Failed to read existing index: {e}. Reinitializing clean index.")

        logger.info(f"Creating fresh FAISS IndexIDMap2(IndexFlatIP) with dim={self.dimension}")
        sub_index = faiss.IndexFlatIP(self.dimension)
        self.index = faiss.IndexIDMap2(sub_index)
        self.faiss_to_chunk = {}
        self.chunk_to_faiss = {}
        self.next_faiss_id = 1
        self.save()

    def save(self):
        """Serializes FAISS index and ID mapping to disk."""
        with self._lock:
            try:
                faiss.write_index(self.index, self.index_file)
                meta = {
                    "faiss_to_chunk": {str(k): v for k, v in self.faiss_to_chunk.items()},
                    "chunk_to_faiss": self.chunk_to_faiss,
                    "next_faiss_id": self.next_faiss_id
                }
                with open(self.metadata_file, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2)
                logger.info(f"Persisted FAISS index with {self.index.ntotal} vectors.")
            except Exception as e:
                logger.error(f"Failed to save FAISS index: {e}")

    def add_embeddings(self, chunk_ids: List[str], embeddings: np.ndarray) -> List[int]:
        """
        Adds normalized embeddings with unique integer IDs to the index.
        Returns: list of assigned faiss_ids
        """
        if len(chunk_ids) == 0:
            return []

        if embeddings.shape[0] != len(chunk_ids):
            raise ValueError(f"Mismatch: {embeddings.shape[0]} embeddings for {len(chunk_ids)} chunk IDs.")

        with self._lock:
            assigned_ids = []
            for chunk_id in chunk_ids:
                # Remove prior vector if chunk was already indexed
                if chunk_id in self.chunk_to_faiss:
                    old_id = self.chunk_to_faiss[chunk_id]
                    self.index.remove_ids(np.array([old_id], dtype=np.int64))
                    del self.faiss_to_chunk[old_id]

                fid = self.next_faiss_id
                self.next_faiss_id += 1
                self.faiss_to_chunk[fid] = chunk_id
                self.chunk_to_faiss[chunk_id] = fid
                assigned_ids.append(fid)

            ids_arr = np.array(assigned_ids, dtype=np.int64)
            self.index.add_with_ids(embeddings.astype(np.float32), ids_arr)
            self.save()
            return assigned_ids

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        allowed_chunk_ids: Optional[set] = None
    ) -> List[Tuple[str, float]]:
        """
        Performs inner product (cosine similarity) search on FAISS.
        Returns list of (chunk_id, similarity_score).
        """
        if self.index.ntotal == 0:
            return []

        # Ensure 2D shape (1, dimension)
        if len(query_embedding.shape) == 1:
            query_embedding = np.expand_dims(query_embedding, axis=0)

        # Retrieve more candidates if filtering is active
        fetch_k = min(self.index.ntotal, top_k * 4 if allowed_chunk_ids else top_k)

        with self._lock:
            scores, indices = self.index.search(query_embedding.astype(np.float32), fetch_k)

        results: List[Tuple[str, float]] = []
        for score, fid in zip(scores[0], indices[0]):
            if fid == -1:
                continue
            chunk_id = self.faiss_to_chunk.get(int(fid))
            if not chunk_id:
                continue

            if allowed_chunk_ids is not None and chunk_id not in allowed_chunk_ids:
                continue

            results.append((chunk_id, float(score)))
            if len(results) >= top_k:
                break

        return results

    def remove_chunks(self, chunk_ids: List[str]):
        """
        Removes vectors corresponding to chunk_ids from FAISS and metadata.
        """
        if not chunk_ids:
            return

        with self._lock:
            fids_to_remove = []
            for cid in chunk_ids:
                if cid in self.chunk_to_faiss:
                    fid = self.chunk_to_faiss[cid]
                    fids_to_remove.append(fid)
                    del self.chunk_to_faiss[cid]
                    if fid in self.faiss_to_chunk:
                        del self.faiss_to_chunk[fid]

            if fids_to_remove:
                self.index.remove_ids(np.array(fids_to_remove, dtype=np.int64))
                self.save()
                logger.info(f"Removed {len(fids_to_remove)} vectors from FAISS index.")

    def reset_index(self):
        """Clears all vectors and resets index."""
        with self._lock:
            sub_index = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIDMap2(sub_index)
            self.faiss_to_chunk = {}
            self.chunk_to_faiss = {}
            self.next_faiss_id = 1
            self.save()
            logger.info("Reset FAISS index to empty state.")
