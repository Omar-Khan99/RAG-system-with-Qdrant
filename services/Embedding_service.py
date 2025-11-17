from ollama import Client
from typing import Optional, Dict, Any, List
from config.settings import settings
class EmbeddingSrevice:
    def __init__(self):
        self.ollama = Client(host="http://ollama:11434")
        self.embedding_model = settings.MODEL_EMBEDDING_NAME

    def get_embedding_dimension(self) -> int:
        emb = self.ollama.embeddings(model= self.embedding_model, prompt= 'text')
        return len(emb['embedding'])


    def get_embedding(self, text: str) -> List[float]:
        try:
            response = self.ollama.embeddings(model= self.embedding_model, prompt= text)
            return response["embedding"]
        except Exception as e:
            raise Exception(f"Error getting embedding: {str(e)}")
