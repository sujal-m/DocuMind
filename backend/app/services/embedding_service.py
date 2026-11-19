import os
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.app.core.config import settings
from backend.app.core.logging import logger

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            if os.path.exists(settings.LOCAL_MODEL_DIR):
                os.environ["HF_HUB_OFFLINE"] = "1"
                os.environ["TRANSFORMERS_OFFLINE"] = "1"
                model_target = settings.LOCAL_MODEL_DIR
                logger.info(f"Loading embedding model from local workspace directory: {model_target}")
                self._model = SentenceTransformer(model_target, model_kwargs={"local_files_only": True})
            else:
                model_target = settings.EMBEDDING_MODEL_NAME
                logger.info(f"Loading embedding model from name: {model_target}")
                self._model = SentenceTransformer(model_target)
            logger.info("Embedding model loaded successfully.")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embeds a single query or text string into a normalized 1D float32 vector.
        """
        if not text or not text.strip():
            # Return zero vector if empty
            return np.zeros((settings.EMBEDDING_DIMENSION,), dtype=np.float32)

        embedding = self._model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embedding.astype(np.float32)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Embeds a batch of text strings into normalized 2D float32 vectors (N, dimension).
        """
        if not texts:
            return np.empty((0, settings.EMBEDDING_DIMENSION), dtype=np.float32)

        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings.astype(np.float32)
