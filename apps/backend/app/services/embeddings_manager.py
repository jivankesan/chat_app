# app/services/embeddings_manager.py

import numpy as np
import faiss

def normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norm

class EmbeddingsManager:
    """
    Manages a FAISS index for user documents.
    For demonstration, we keep a separate index per user_id in memory.
    """
    def __init__(self):
        self.user_indices = {}  # user_id -> { "faiss_index": ..., "doc_texts": [...], "embeddings": np.ndarray }

    def create_index_for_user(self, user_id: str, embeddings: np.ndarray, doc_texts: list[str]):
        embeddings = embeddings.astype('float32')
        embeddings = normalize_embeddings(embeddings)
        dimension = embeddings.shape[1]

        faiss_index = faiss.IndexFlatIP(dimension)
        faiss_index.add(embeddings)

        self.user_indices[user_id] = {
            "faiss_index": faiss_index,
            "doc_texts": doc_texts,
            "embeddings": embeddings
        }

    def add_embeddings_for_user(self, user_id: str, embeddings: np.ndarray, doc_texts: list[str]):
        if user_id not in self.user_indices:
            self.create_index_for_user(user_id, embeddings, doc_texts)
        else:
            user_data = self.user_indices[user_id]
            old_index = user_data["faiss_index"]
            old_texts = user_data["doc_texts"]
            old_embeddings = user_data["embeddings"]

            embeddings = embeddings.astype('float32')
            embeddings = normalize_embeddings(embeddings)

            new_embeddings = np.concatenate([old_embeddings, embeddings], axis=0)
            old_index.add(embeddings)

            user_data["doc_texts"] = old_texts + doc_texts
            user_data["embeddings"] = new_embeddings

    def search_user_index(self, user_id: str, query_embedding: np.ndarray, k=5) -> str:
        if user_id not in self.user_indices:
            return ""

        query_embedding = np.array(query_embedding).astype('float32')
        query_embedding = normalize_embeddings(query_embedding.reshape(1, -1))

        faiss_index = self.user_indices[user_id]["faiss_index"]
        doc_texts = self.user_indices[user_id]["doc_texts"]

        distances, indices = faiss_index.search(query_embedding, k)
        content = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            content.append(doc_texts[idx])
        return "\n\n".join(content)