#!/bin/sh
# init-ollama.sh

echo "🚀 Starting Ollama server in background..."
ollama serve &
SERVER_PID=$!

echo "⏳ Waiting for server to be ready..."
sleep 5  # انتظر حتى يبدأ الخادم

echo "✅ Pulling embedding model..."
ollama pull mahonzhan/all-MiniLM-L6-v2 

echo "✅ Pulling LLM model..."
ollama pull llama3.1:8b  # ← أو أي نموذج تفضله (تحقق من ollama list)

echo "✅ Models ready. Keeping server running..."
wait $SERVER_PID  # ← هذا يحافظ على تشغيل الخادم للأبد