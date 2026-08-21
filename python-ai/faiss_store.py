import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer

# We import faiss inside classes or try-except blocks to catch import errors gracefully.
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[Warning] FAISS library not found. A numpy-based cosine similarity index will serve as fallback.")
# Configure path to knowledgebase directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGEBASE_DIR = os.path.join(BASE_DIR, "knowledgebase")

class NumpyVectorStore:
    """
    A pure NumPy/JSON fallback vector store in case FAISS installation encounters issues.
    Matches FAISS functionality exactly.
    """
    def __init__(self, directory: str = KNOWLEDGEBASE_DIR):
        self.directory = directory
        self.index_path = os.path.join(directory, "numpy_index.npy")
        self.metadata_path = os.path.join(directory, "numpy_metadata.json")
        self.vectors = []
        self.metadata = []
        os.makedirs(self.directory, exist_ok=True)
        self.load()

    def add_documents(self, embeddings: np.ndarray, docs_meta: List[Dict[str, Any]]):
        if len(self.vectors) == 0:
            self.vectors = embeddings
        else:
            self.vectors = np.vstack([self.vectors, embeddings])
        self.metadata.extend(docs_meta)
        self.save()

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        if len(self.vectors) == 0:
            return []
        
        # Calculate cosine similarities
        # Vectors are already L2 normalized, so inner product is cosine similarity
        scores = np.dot(self.vectors, query_vector)
        
        # Get top-K indices
        top_k_idx = np.argsort(scores)[::-1][:k]
        
        results = []
        for idx in top_k_idx:
            # Cosine similarity score range [-1, 1] converted to percentage
            score = float(scores[idx])
            results.append((score, self.metadata[idx]))
        return results

    def save(self):
        if len(self.vectors) > 0:
            np.save(self.index_path, self.vectors)
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2)

    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.vectors = np.load(self.index_path)
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"Error loading numpy fallback index: {e}")
                self.vectors = []
                self.metadata = []

    def clear(self):
        self.vectors = []
        self.metadata = []
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.metadata_path):
            os.remove(self.metadata_path)

class FAISSVectorStore:
    def __init__(self, directory: str = KNOWLEDGEBASE_DIR, dimension: int = 384):
        self.directory = directory
        self.dimension = dimension
        self.index_path = os.path.join(directory, "faiss_index.bin")
        self.metadata_path = os.path.join(directory, "faiss_metadata.json")
        self.index = None
        self.metadata = []
        self.fallback = NumpyVectorStore(directory=directory)
        os.makedirs(self.directory, exist_ok=True)
        self.load()

    def _init_index(self):
        if FAISS_AVAILABLE:
            # IndexFlatIP uses Inner Product (for normalized vectors, IP is equivalent to Cosine Similarity)
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            self.index = None

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]):
        if not embeddings:
            return
            
        embeddings_np = np.array(embeddings, dtype=np.float32)
        # Normalize vectors for Cosine Similarity (Inner Product of normalized vectors)
        norms = np.linalg.norm(embeddings_np, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1.0, norms)
        embeddings_np = embeddings_np / norms

        # Create combined metadata list
        docs_meta = []
        for doc, meta in zip(documents, metadatas):
            meta_combined = dict(meta)
            meta_combined["chunk_content"] = doc
            docs_meta.append(meta_combined)

        if FAISS_AVAILABLE:
            try:
                if self.index is None:
                    self._init_index()
                self.index.add(embeddings_np)
                self.metadata.extend(docs_meta)
                self.save()
            except Exception as e:
                print(f"FAISS indexing failed: {e}. Falling back to NumPy Vector Store.")
                self.fallback.add_documents(embeddings_np, docs_meta)
        else:
            self.fallback.add_documents(embeddings_np, docs_meta)

    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        query_np = np.array(query_embedding, dtype=np.float32)
        norm = np.linalg.norm(query_np)
        if norm > 0:
            query_np = query_np / norm

        if FAISS_AVAILABLE and self.index is not None and self.index.ntotal > 0:
            try:
                # Reshape query to 2D array
                query_np = np.expand_dims(query_np, axis=0)
                scores, indices = self.index.search(query_np, k)
                
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx < 0 or idx >= len(self.metadata):
                        continue
                    results.append({
                        "score": float(score),
                        "metadata": self.metadata[idx]
                    })
                return results
            except Exception as e:
                print(f"FAISS search failed: {e}. Searching fallback.")
                fallback_results = self.fallback.search(query_np, k)
                return [{"score": score, "metadata": meta} for score, meta in fallback_results]
        else:
            fallback_results = self.fallback.search(query_np, k)
            return [{"score": score, "metadata": meta} for score, meta in fallback_results]

    def save(self):
        if FAISS_AVAILABLE and self.index is not None:
            try:
                faiss.write_index(self.index, self.index_path)
                with open(self.metadata_path, "w", encoding="utf-8") as f:
                    json.dump(self.metadata, f, indent=2)
            except Exception as e:
                print(f"Failed to write FAISS index files: {e}")

    def load(self):
        if FAISS_AVAILABLE and os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                print(f"FAISS database loaded successfully with {self.index.ntotal} records.")
            except Exception as e:
                print(f"Failed to read FAISS index files: {e}. Initializing empty.")
                self._init_index()
                self.metadata = []
        else:
            self._init_index()
            self.metadata = []

    def clear(self):
        self.metadata = []
        self._init_index()
        self.fallback.clear()
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.metadata_path):
            os.remove(self.metadata_path)

# Initialize global FAISS instance
faiss_store = FAISSVectorStore()
