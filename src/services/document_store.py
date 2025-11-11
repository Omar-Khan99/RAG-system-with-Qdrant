# src/services/document_store.py
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from .document_processor import DocumentProcessor
from src.config.settings import settings
from typing import List, Dict, Any
import os
import hashlib

class QdrantDocumentStore:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST, 
            port=settings.QDRANT_PORT
        )
        self.collection_name = settings.COLLECTION_NAME
        self.doc_processor = DocumentProcessor(settings.MODEL_NAME)
        self._ensure_collection()
    
    def _ensure_collection(self):
        """إنشاء المجموعة إذا لم تكن موجودة"""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.doc_processor.model.get_sentence_embedding_dimension(),
                    distance=Distance.COSINE
                ),
            )
            print(f"Collection '{self.collection_name}' created")
    
    def _generate_point_id(self, file_path: str, chunk_id: int) -> int:
        """إنشاء معرف فريد للنقطة"""
        unique_string = f"{file_path}_{chunk_id}"
        return int(hashlib.md5(unique_string.encode()).hexdigest()[:15], 16)
    
    def upload_document(self, file_path: str, chunk_size: int = 500) -> bool:
        """رفع ومعالجة مستند واحد"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"Processing document: {file_path}")
        
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
        embeddings = self.doc_processor.model.encode(chunk_texts).tolist()
        
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
        
        print(f"Successfully uploaded {len(points)} chunks from {file_path}")
        return True
    
    def search_documents(self, query: str, limit: int = 10, score_threshold: float = 0.5):
        """البحث عن محتوى مشابه في المستندات"""
        query_embedding = self.doc_processor.model.encode([query]).tolist()[0]
        
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            with_vectors=True,
            with_payload=True,
            limit=limit,
            score_threshold=score_threshold
        ).points
        
        return search_results
    
    def get_collection_info(self):
        """الحصول على معلومات المجموعة"""
        return self.client.get_collection(self.collection_name)