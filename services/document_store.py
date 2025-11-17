# src/services/document_store.py
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from .document_processor import DocumentProcessor
from config.settings import settings
from typing import List, Dict, Any
from .Embedding_service import EmbeddingSrevice
import os
import hashlib
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http import models as rest

logger = logging.getLogger(__name__)

class QdrantDocumentStore:
    def __init__(self):
        self.embedding = EmbeddingSrevice()
        self.client = QdrantClient(
            host=settings.QDRANT_HOST, 
            port=settings.QDRANT_PORT
        )
        self.collection_name = settings.COLLECTION_NAME
        self.doc_processor = DocumentProcessor()
        self._ensure_collection()
    
    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")
        except (UnexpectedResponse, ValueError):
            # لم تُوجد → ننشئها
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=rest.VectorParams(
                    size=self.embedding.get_embedding_dimension(),  # حسب نموذج الـ embedding
                    distance=rest.Distance.COSINE,
                ),
            )
            logger.info(f"Collection '{self.collection_name}' created.")
    
    def _generate_point_id(self, file_path: str, chunk_id: int) -> int:
        """إنشاء معرف فريد للنقطة"""
        unique_string = f"{file_path}_{chunk_id}"
        return int(hashlib.md5(unique_string.encode()).hexdigest()[:15], 16)
    
    def upload_document(self, file_path: str, chunk_size: int = 500) -> bool:
        """رفع ومعالجة مستند واحد"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Processing document: {file_path}")
        
        # استخراج النص من المستند
        text = self.doc_processor.process_document(file_path)
        if not text.strip():
            raise ValueError(f"No text extracted from: {file_path}")
                
        # تقسيم النص إلى أجزاء
        chunks = self.doc_processor.chunk_text(text, chunk_size, settings.CHUNK_OVERLAP)
        chunk_texts = [chunk['text'] for chunk in chunks]
        full_text = ' '.join(chunk_texts)

        # استخراج البيانات الوصفية
        metadata = self.doc_processor.extract_metadata(file_path, full_text)
        
        # توليد التضمينات النصية
        embeddings = [self.embedding.get_embedding(chunk) for chunk in chunk_texts]        

        # إعداد النقاط لـ Qdrant
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_metadata = metadata.copy()
            point_metadata.update({
                'chunk_id': idx,
                'chunk_text': chunk['text'],
                'total_words': chunk['total_words'],
                'is_chunk': True,
                'original_text_preview': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
            })
            
            point = PointStruct(
                id=self._generate_point_id(file_path, idx),
                vector=embedding,
                payload=point_metadata
            )
            points.append(point)
        
        # رفع إلى Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"Successfully uploaded {len(points)} chunks from {file_path}")
        return True
    
    def search_documents(self, query: str, limit: int = 10, score_threshold: float = 0.5):
        """البحث عن محتوى مشابه في المستندات"""
        query_embedding = self.embedding.get_embedding(query)
        
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            with_vectors=True,
            with_payload=True,
            limit=limit,
            score_threshold=score_threshold
        )
        
        return search_results
    
    def get_collection_info(self):
        """الحصول على معلومات المجموعة"""
        return self.client.get_collection(self.collection_name)