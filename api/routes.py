# src/api/routes.py
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import os
from datetime import datetime
import logging
from services.document_store import QdrantDocumentStore


router = APIRouter()
doc_store = QdrantDocumentStore()
logger = logging.getLogger(__name__)


@router.post("/upload-file/")
async def upload_file(
    file: UploadFile = File(...), 
    chunk_size: int = Query(500, ge=100, le=2000)
):
    """رفع ملف جديد ومعالجته"""
    try:
        # إنشاء اسم ملف مؤقت فريد
        file_extension = f'{file.filename}'
        
        # Save uploaded file
        with open(file_extension, "wb") as f:
            content = await file.read()
            f.write(content)
            
        # process document
        success = doc_store.upload_document(file_extension,chunk_size)

        logger.info(f"File '{file.filename}' uploaded and processed successfully.")
        # clean up
        os.remove(file.filename)

        if success:
            return JSONResponse(
                status_code= 200,
                content={
                    "message": "File uploaded successfully",
                    "file_name": file.filename,
                    "file_size": len(content),
                    "chunk_size": chunk_size,
                    "upload_time": datetime.now().isoformat()
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to process file")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/search/")
async def search_semantic(
    query: str = Query(...),
    limit: int = Query(10, ge=1, le=20),
    score_threshold: float = Query(0.25, ge=0.1, le=1.0),
    include_chunks: bool = Query(True),
    include_vectors: bool = Query(False)
):
    """البحث الدلالي في المستندات"""
    try:
        search_results = doc_store.search_documents(query, limit, score_threshold)

        response = {
            'query': query,
            'total_results': len(search_results),
            'result': []
        }

        for result in search_results:
            result_data = {
                "score": float(result.score),
                "file_name": result.payload.get('file_name'),
                "file_type": result.payload.get('file_type'),
                "file_size": result.payload.get('file_size'),
                "chunk_id": result.payload.get('chunk_id'),
                "metadata": {
                    "processed_date": result.payload.get('processed_date'),
                    "total_words": result.payload.get('total_words'),
                    "total_chars": result.payload.get('total_chars')
                }
            }

            if include_chunks:
                result_data['chunk_text'] = result.payload.get('chunk_text')
                result_data["original_text_preview"] = result.payload.get('original_text_preview')
                #result_data["start_word"] = result.payload.get('start_word')
                #result_data["end_word"] = result.payload.get('end_word')
                result_data['total_words'] =  result.payload.get('total_words')

            if include_vectors:
                result_data['vectors'] = result.vector
            
            response["result"].append(result_data)
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/")
async def list_files(
    file_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """قائمة جميع الملفات مع pagination"""
    try:
        all_files = {}
        
        search_results = doc_store.client.scroll(
            collection_name=doc_store.collection_name,
            limit=1000
        )
        
        for point in search_results[0]:
            file_name = point.payload.get('file_name')
            if file_name not in all_files:
                all_files[file_name] = {
                    "file_name": file_name,
                    "file_path": point.payload.get('file_path'),
                    "file_type": point.payload.get('file_type'),
                    "file_size": point.payload.get('file_size'),
                    "processed_date": point.payload.get('processed_date'),
                    "total_chunks": 0,
                    "total_words": point.payload.get('total_words'),
                    "total_chars": point.payload.get('total_chars'),
                    "chunks": []
                }
            
            all_files[file_name]["total_chunks"] += 1
            all_files[file_name]["chunks"].append({
                "chunk_id": point.payload.get('chunk_id'),
                'total_words': point.payload.get('total_words'),
                "text_preview": point.payload.get('original_text_preview'),
                "vector_id": point.id
            })
        
        files_list = list(all_files.values())
        if file_type:
            files_list = [f for f in files_list if f['file_type'] == f'.{file_type}']
        
        paginated_files = files_list[offset:offset + limit]
        
        return JSONResponse(
            status_code=200,
            content={
            "total_files": len(files_list),
            "files": paginated_files,
            "pagination": {
                "limit": limit,
                "has_more": (limit) < len(files_list)
            }}
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_name}/")
async def get_file_chunks(
    file_name: str,
    include_text: bool = Query(True)
):
    """الحصول على جميع أجزاء ملف معين"""
    try:
        search_results = doc_store.client.scroll(
            collection_name=doc_store.collection_name,
            scroll_filter={
                "must": [
                    {
                        "key": "file_name",
                        "match": {"value": file_name}
                    }
                ]
            }
        )
        
        if not search_results[0]:
            raise HTTPException(status_code=404, detail="File not found")

        chunks = []
        for point in search_results[0]:
            chunk_data = {
                "chunk_id": point.payload.get('chunk_id'),
                'total_words': point.payload.get('total_words'),
                "vector_id": point.id,
                "score": None
            }
            
            if include_text:
                chunk_data["text"] = point.payload.get('chunk_text')
                chunk_data["text_preview"] = point.payload.get('original_text_preview')
            
            chunks.append(chunk_data)
        
        return {
            "file_name": file_name,
            "total_chunks": len(chunks),
            "chunks": chunks
        }
        
    except Exception as e:
        raise Exception(f"Error Not found file: {str(e)}")

@router.get("/chunks/{chunk_id}/")
async def get_chunk_detail(chunk_id: int, file_name: str):
    """الحصول على تفاصيل جزء معين"""
    try:
        search_results = doc_store.client.scroll(
            collection_name=doc_store.collection_name,
            scroll_filter={
                "must": [
                    {
                        "key": "chunk_id",
                        "match": {"value": chunk_id}
                    },
                    {
                        "key": "file_name", 
                        "match": {"value": file_name}
                    }
                ]
            },
            with_vectors=True,
            limit=1
        )
        
        if not search_results[0]:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        point = search_results[0][0]
        
        return JSONResponse(
            status_code=200,
            content={
            "chunk_id": chunk_id,
            "file_name": file_name,
            "metadata": {
                "file_type": point.payload.get('file_type'),
                "file_size": point.payload.get('file_size'),
                "processed_date": point.payload.get('processed_date'),
                "total_words": point.payload.get('total_words'),
                "total_chars": point.payload.get('total_chars')
            },
            "content": {
                "full_text": point.payload.get('chunk_text'),
                "preview": point.payload.get('original_text_preview')
            },
            "vector_info": {
                "vector_id": point.id,
                "vector_dimension": len(point.vector) if point.vector else 0,
                "vector": point.vector if point.vector else 0
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{file_name}/")
async def delete_file(file_name: str):
    """حذف ملف وجميع أجزائه"""
    try:
        search_results = doc_store.client.scroll(
            collection_name=doc_store.collection_name,
            scroll_filter={
                "must": [
                    {
                        "key": "file_name",
                        "match": {"value": file_name}
                    }
                ]
            },
            limit=1000
        )
        
        point_ids = [point.id for point in search_results[0]]
        
        if point_ids:
            doc_store.client.delete(
                collection_name=doc_store.collection_name,
                points_selector=point_ids
            )
        
        return {
            "message": f"File '{file_name}' deleted successfully",
            "deleted_chunks": len(point_ids),
            "deleted_points": point_ids
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))