FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# تثبيت الأدوات النظامية و uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir uv

# نسخ ملفات التبعيات
COPY pyproject.toml uv.lock ./

# تثبيت الحزم في virtual environment باستخدام uv
RUN uv sync --frozen

# نسخ باقي الملفات (بعد التثبيت!)
COPY . .

# لا حاجة لضبط PATH إذا استخدمت `uv run`
EXPOSE 8000

# الافتراضي (للبناء بدون compose override)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]