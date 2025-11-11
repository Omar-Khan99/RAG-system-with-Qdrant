🧠 RAG System with Qdrant
=========================

This project implements a **Retrieval-Augmented Generation (RAG)** system using **Qdrant** as the vector database and **FastAPI** as the backend.It allows users to query a large knowledge base and retrieve semantically relevant chunks of information before generating responses using a language model.

🚀 Features
-----------

*   **RAG Architecture:** Combines vector search with LLM inference for accurate, context-aware responses.
    
*   **Qdrant Integration:** Efficient and scalable vector similarity search.
    
*   **FastAPI Backend:** Lightweight and high-performance API framework.
    
*   **Dockerized Environment:** Ready-to-run setup for both development and production.
    
*   **uv-based Dependency Management:** Ultra-fast Python package manager for modern environments.
    

⚙️ Prerequisites
----------------

Before running the project, make sure you have the following installed:

*   [Docker](https://www.docker.com/)
    
*   [Docker Compose](https://docs.docker.com/compose/)
    
*   (Optional for local dev) [uv](https://docs.astral.sh/uv/?utm_source=chatgpt.com)
    

🧰 Local Development Setup (Using uv)
-------------------------------------

If you want to run the app locally (without Docker):


``` bash 
# Install uv if not installed  
curl -LsSf https://astral.sh/uv/install.sh | sh  

# Sync dependencies  
uv sync --locked  

# Run the FastAPI app  
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload   
 ```

Then open your browser at 👉 http://localhost:8000/docs

🐳 Running with Docker
----------------------

### 1️⃣ Build and start the containers

``` bash
docker-compose up --build
```
This will:

*   Start a **Qdrant** container (vector DB).
    
*   Build and start the **FastAPI app**.
    
*   Expose the API on http://localhost:8000.
    

### 2️⃣ Stop the containers

```  bash 
docker-compose down   
```

🧠 How It Works
---------------

1.  **Data Ingestion:** Text documents are embedded into vector representations using an embedding model and stored in Qdrant.
    
2.  **Retrieval:** When a user sends a query, the system retrieves the most relevant documents from Qdrant using vector similarity search.
    
3.  **Generation:** The retrieved context is fed into a large language model (LLM) to generate an informed, context-aware response.
    

🧩 Useful Commands
------------------

``` bash 
# Sync dependencies  
uv sync --locked  

# Run FastAPI app  
uv run uvicorn src.main:app --reload  

# Rebuild Docker images  
docker-compose build  

# Start Qdrant only  
docker-compose up qdrant  
```


🛠 Future Improvements
----------------------

*   Add frontend dashboard for querying.
    
*   Integrate advanced embedding models (OpenAI, SentenceTransformers, etc.).
    
*   Include caching and metadata filtering in retrieval.
    
*   CI/CD pipeline with GitHub Actions.