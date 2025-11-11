# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# نسخ المتطلبات أولاً للاستفادة من caching
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY src/ ./src/

# التعرض للمنفذ
EXPOSE 8000

# تشغيل التطبيق
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]