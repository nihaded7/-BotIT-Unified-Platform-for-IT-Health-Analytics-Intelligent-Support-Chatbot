import re
from typing import Tuple, Optional

import numpy as np
import pandas as pd

try:
    import faiss  # type: ignore
except Exception as _e:  # pragma: no cover
    faiss = None  # lazy fallback; will raise at runtime if used without install

try:
    from sentence_transformers import SentenceTransformer
except Exception as _e:  # pragma: no cover
    SentenceTransformer = None  # lazy fallback; will raise at runtime if used without install


class RetrievalSystem:
    """
    Embeddings-based retrieval over a CSV knowledge base using FAISS (inner product on L2-normalized vectors).

    Interface is compatible with the previous TF-IDF implementation: `search(query, top_k, threshold)`
    returns (tech_response, score, matched_issue) with `score` in [0, 1] approximating cosine similarity.
    """

    def __init__(self, dataset_path: str, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if SentenceTransformer is None or faiss is None:
            raise ImportError(
                "Embeddings retrieval requires 'sentence-transformers' and 'faiss-cpu'. Please install dependencies."
            )

        self.df = pd.read_csv(dataset_path)

        if "Customer_Issue" not in self.df.columns or "Tech_Response" not in self.df.columns:
            raise ValueError("Dataset must contain 'Customer_Issue' and 'Tech_Response' columns")

        # Clean a lightweight version of the issue for better matching
        def clean_issue(x: str) -> str:
            x = str(x).lower()
            x = re.sub(r"\(issue \d+\)", "", x)
            x = re.sub(r"\s+", " ", x).strip()
            return x

        # Create cleaned issue column and handle NaNs/empties robustly
        self.df["__clean_issue__"] = (
            self.df["Customer_Issue"].fillna("").apply(clean_issue)
        )

        # Filter out rows with completely empty cleaned issues to avoid useless vectors
        self.df = self.df[self.df["__clean_issue__"].str.len() > 0].reset_index(drop=True)
        if self.df.empty:
            raise ValueError("No valid issues to index after cleaning; check dataset contents")

        # Load embedding model once
        self.model_name = embedding_model
        self.model = SentenceTransformer(self.model_name)

        # Encode all issues
        issue_texts = self.df["__clean_issue__"].astype(str).tolist()
        embeddings = self.model.encode(issue_texts, convert_to_numpy=True, normalize_embeddings=True)

        # Build FAISS index (inner product == cosine on normalized vectors)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings.astype(np.float32))

    def _encode_query(self, text: str) -> np.ndarray:
        vec = self.model.encode([str(text)], convert_to_numpy=True, normalize_embeddings=True)
        return vec.astype(np.float32)

    def search(self, query: str, top_k: int = 1, threshold: float = 0.5) -> Tuple[Optional[str], float, Optional[str]]:
        """
        Returns (tech_response, score, matched_issue) if best score >= threshold, else (None, score, None).
        Score is cosine similarity in [0, 1] (clipped for safety).
        """
        if query is None or str(query).strip() == "":
            return None, 0.0, None

        q = self._encode_query(query)
        scores, idxs = self.index.search(q, max(1, top_k))  # shapes: (1, k)
        scores = scores[0]
        idxs = idxs[0]

        # Take best hit
        best_idx = int(idxs[0])
        best_score = float(np.clip(scores[0], 0.0, 1.0))

        if best_idx < 0 or best_idx >= len(self.df):
            return None, 0.0, None

        if best_score >= threshold:
            row = self.df.iloc[best_idx]
            return row["Tech_Response"], best_score, row["Customer_Issue"]
        return None, best_score, None
