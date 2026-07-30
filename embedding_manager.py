import numpy as np
import hashlib
from typing import List
from backend.app.config import settings

class FallbackEmbedder:
    """
    A lightweight, dependency-free embedding generator.
    Creates deterministic vectors using string hashing (TF-IDF approximation).
    Useful for local testing if APIs or PyTorch/SentenceTransformers are unavailable.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _text_to_vector(self, text: str) -> np.ndarray:
        # Simple deterministic hashing-based tokenization & projection
        vector = np.zeros(self.dimension)
        words = text.lower().split()
        if not words:
            return vector
            
        for word in words:
            # Hash word to get deterministic index and weight
            hash_val = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            index = hash_val % self.dimension
            weight = 1.0 + (hash_val % 10) / 10.0
            vector[index] += weight
            
        # Normalize L2
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

    def embed_query(self, text: str) -> List[float]:
        return self._text_to_vector(text).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]

class EmbeddingManager:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER.lower()
        self.local_model = None
        self.openai_client = None
        self.gemini_client = None
        self.fallback = FallbackEmbedder(dimension=384)
        
        self._initialize_provider()

    def _initialize_provider(self):
        # 1. Local Sentence Transformers
        if self.provider == "local":
            try:
                from sentence_transformers import SentenceTransformer
                # Use MiniLM as it's lightweight (approx 80MB)
                self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Loaded SentenceTransformer ('all-MiniLM-L6-v2') successfully.")
            except Exception as e:
                print(f"Failed to load sentence-transformers: {e}. Falling back to default embedder.")
                self.provider = "fallback"

        # 2. OpenAI API
        elif self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                print("OpenAI API key missing. Falling back to default embedder.")
                self.provider = "fallback"
            else:
                try:
                    from openai import OpenAI
                    self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                except Exception as e:
                    print(f"Failed to initialize OpenAI client: {e}. Falling back to default.")
                    self.provider = "fallback"

        # 3. Gemini API
        elif self.provider == "gemini":
            if not settings.GEMINI_API_KEY:
                print("Gemini API key missing. Falling back to default embedder.")
                self.provider = "fallback"
            else:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    self.gemini_client = genai
                except Exception as e:
                    print(f"Failed to initialize Gemini client: {e}. Falling back to default.")
                    self.provider = "fallback"

    def embed_query(self, text: str) -> List[float]:
        if not text:
            return [0.0] * 384
            
        if self.provider == "local" and self.local_model:
            try:
                return self.local_model.encode(text).tolist()
            except Exception as e:
                print(f"SentenceTransformer embedding error: {e}")
                return self.fallback.embed_query(text)
                
        elif self.provider == "openai" and self.openai_client:
            try:
                response = self.openai_client.embeddings.create(
                    input=[text],
                    model="text-embedding-3-small"
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"OpenAI embedding error: {e}")
                return self.fallback.embed_query(text)
                
        elif self.provider == "gemini" and self.gemini_client:
            try:
                result = self.gemini_client.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_query"
                )
                return result['embedding']
            except Exception as e:
                print(f"Gemini embedding error: {e}")
                return self.fallback.embed_query(text)
                
        return self.fallback.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
            
        if self.provider == "local" and self.local_model:
            try:
                return self.local_model.encode(texts).tolist()
            except Exception as e:
                print(f"SentenceTransformer batch embedding error: {e}")
                return self.fallback.embed_documents(texts)
                
        elif self.provider == "openai" and self.openai_client:
            try:
                response = self.openai_client.embeddings.create(
                    input=texts,
                    model="text-embedding-3-small"
                )
                return [d.embedding for d in response.data]
            except Exception as e:
                print(f"OpenAI batch embedding error: {e}")
                return self.fallback.embed_documents(texts)
                
        elif self.provider == "gemini" and self.gemini_client:
            try:
                result = self.gemini_client.embed_content(
                    model="models/embedding-001",
                    content=texts,
                    task_type="retrieval_document"
                )
                return result['embeddings']
            except Exception as e:
                print(f"Gemini batch embedding error: {e}")
                return self.fallback.embed_documents(texts)
                
        return self.fallback.embed_documents(texts)

embedding_manager = EmbeddingManager()
