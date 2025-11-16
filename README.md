# 🧠 RAG System with Qdrant & Ollama

A production-ready **Retrieval-Augmented Generation (RAG)** system built with:
- **Qdrant** — high-performance vector database  
- **Ollama** — local LLM & embedding inference  
- **FastAPI** — modern REST API backend  
- **Docker Compose** — fully containerized, reproducible deployment

✅ **Fully working out-of-the-box** — models & data persist between restarts.

---

## 🚀 Features

- ✅ **True offline RAG**: Runs 100% locally using Ollama (no cloud APIs)
- ✅ **Persistent storage**: Qdrant data + Ollama models survive restarts
- ✅ **Semantic search + LLM generation** in one pipeline
- ✅ **Hot-reload** for development (`--reload`)
- ✅ **Docker-first design** — no Python/env setup needed on host
- ✅ Optimized with `uv` for ultra-fast dependency resolution & locking

---

## ⚙️ Prerequisites

Install these **once** on your machine:

| Tool | Purpose | Install Guide |
|------|---------|---------------|
| 🐳 **Docker** | Container runtime | [docker.com](https://www.docker.com/products/docker-desktop) |
| 🐳 **Docker Compose** | Multi-container orchestration | Included in Docker Desktop (v2.20+) |

> ✅ No Python, `uv`, or Ollama installation needed on your host OS — everything runs in containers.

---

## ▶️ Quick Start (Recommended)

### 1. Clone & enter the project
``` bash
git clone https://github.com/Omar-Khan99/RAG-system-with-Qdrant.git
cd RAG-system-with-Qdrant
```

### 2. Start the system (first run = downloads models)
``` bash
docker compose up --build
```
⏳ First run takes time (downloads `all-minilm:l6-v2` + `llama3:8b` ~5GB), but subsequent runs are instant.

### 3. Use the API
Once you see:

```
ollama-1  | ✅ Models ready. Keeping server running...
app-1     | INFO:     Uvicorn running on http://0.0.0.0:8000
```

Open in your browser:

🔹 [Swagger UI (interactive docs)](http://localhost:8000/docs) 

 🔹 [Qdrant Dashboard](http://localhost:6333/dashboard)

---

## 🔁 Daily Workflow (Fast Restart)
After first setup, use these for quick stop/start without re-downloading:

| COMMAND | DESCRIPTION |
|------|--------------|
| `docker compose down` | ✅ **Stop services** (keeps data & models!) |
| `docker compose up` | ✅ **Restart in <10 seconds** (no rebuild, no redownload) |
`docker compose up -d` | Run in background (detached mode) |
`docker compose logs -f app` | Stream app logs only

> "💡 Never use -v with down unless you want to wipe all data/models. "

## 🧪 API Endpoints

| ENDPOINT | METHOD | DESCRIPTION |
|------|---------|---------------|
| `/docs`| GET | Interactive API documentation (Swagger UI)
 |
| `/api/v1/upload-file/` | POST | Upload PDF/text and index into Qdrant
 | `/ask` | POST |  Ask questions: `?query=What is Bayanat?&limit=5` |
  `/api/v1/files/` | GET | List uploaded documents


## 🧠 How It Works

1. **Document Upload:** PDF/text → chunked → embedded with `all-minilm:l6-v2` → stored in **Qdrant**

2. **Query:** User question → embedded → top-k similar chunks retrieved from Qdrant

3. **Generation:** Chunks + question → sent to `llama3:8b` via **Ollama** → final answer

> "All models run locally on your machine — no external API calls. "