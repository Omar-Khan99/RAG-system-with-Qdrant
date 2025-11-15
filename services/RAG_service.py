import ollama
from typing import Any, List, Dict
from services.document_store import QdrantDocumentStore

class RAGService:
    def __init__(self, document_store: QdrantDocumentStore):
        self.document_store = document_store
        self.llm_model = "gpt-oss:20b"
        self.embedding_model = 'mahonzhan/all-MiniLM-L6-v2'

    def get_embedding(self, text: str) -> List[float]:
        try:
            response = ollama.embeddings(model= self.embedding_model, prompt= text)
            return response["embedding"]
        except Exception as e:
            raise Exception(f"Error getting embedding: {str(e)}")

    
    def search_similar_chunks(self, query: str, limit: int = 5) -> List[Dict[str,Any]]:
        query_embedding = self.get_embedding(query)

        search_results = self.document_store.client.search(
            collection_name= self.document_store.collection_name,
            query_vector= query_embedding,
            limit = limit
        )

        return [
            {
                'text': result.payload.get('chunk_text'),
                'file_name': result.payload.get('file_name'),
                'score': result.score,
                "chunk_id": result.payload.get("chunk_id")
            }
            for result in search_results
        ]

    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:

        context_text = "\n\n".join([
            f"the file: {chunk['file_name']}\nthe text: {chunk['text']}"
            for chunk in context_chunks
        ])

        prompt = f"""
        Based on the following information, answer the question accurately and clearly.
        If you cannot find the answer in the information provided, say that you do not know.

        Reference information:
        {context_text}

        The question: {query}

        The answer:
        """

        try:
            response = ollama.generate(model= self.llm_model, prompt=prompt)
            return response['response']
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

    def ask_question(self, query: str, limit: int = 5) ->Dict[str,Any]:

        similar_chunks = self.search_similar_chunks(query,limit)

        if similar_chunks:
            answer = self.generate_response(query, similar_chunks)
        else:
            answer = "Sorry, I don't found any enough information for answer you question"

        return {
            "question": query,
            "answer": answer,
            "sources": similar_chunks,
            "total_sources": len(similar_chunks)
        }