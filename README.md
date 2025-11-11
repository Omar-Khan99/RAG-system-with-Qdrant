# Document Search & RAG System

A sophisticated document search and management system using FastAPI and Qdrant vector database.

## Features

- 📄 Support for multiple document types (PDF, DOCX, TXT, PPTX, CSV, Excel)
- 🔍 Semantic search using sentence transformers
- 📚 RAG (Question & Answer)
- 📊 Metadata extraction and management
- 🐳 Dockerized deployment
- 📚 RESTful API

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Start the services:
```bash
docker-compose up -d
```

2. Access the application:
* API: http://localhost:8000
* Documentation: http://localhost:8000/docs
* Qdrant Dashboard: http://localhost:6333/dashboard

### API Endpoints
* `POST /upload-file/` - Upload and process documents

* `GET /search/` - Semantic search in documents

* `GET /files/` - List all files with pagination

* `GET /files/{file_name}/` - Get chunks of specific file

* `GET /chunks/{chunk_id}/` - Get chunk details

* `POST /ask/` - Ask question (RAG)

* `DELETE /files/{file_name}/` - Delete file and all chunks