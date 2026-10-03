# Legal-tech platform — FastAPI + Jinja2 web app + Qdrant (RAG) + Gemini/Ollama
#
# DIFF vs ANPR's Dockerfile:
#   - No ffmpeg/libgl1/opencv system deps — this app has no video/image
#     pipeline, so we drop that whole apt-get block. Fewer system deps =
#     smaller image, faster build.
#   - EXPOSE 5050, not 4000 — matches this app's settings.PORT default
#     (app/core/config.py), not an arbitrary choice.
#   - HEALTHCHECK hits "/" instead of "/docs" — pick whatever route always
#     returns 200 in YOUR app; "/docs" happened to be right for ANPR only
#     because FastAPI auto-generates it.
FROM python:3.10-slim

WORKDIR /app

# Same pattern as ANPR: requirements first for layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Same pattern as ANPR: app code copied after deps.
# .dockerignore (below) is what keeps .env, .git, qdrant/, legal_tech.db
# and uploads/ OUT of this layer — COPY . . only grabs what's left.
COPY . .

# Runtime-writable dirs — same idea as ANPR's outputImgs/logs, different
# actual folders because this app writes different things.
RUN mkdir -p uploads outputImgs/exports outputImgs/reports logs
RUN useradd -m appuser \
    && mkdir -p /home/appuser/.cache/huggingface \
    && chown -R appuser:appuser /app /home/appuser
USER appuser

EXPOSE 5050

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:5050/').status==200 else sys.exit(1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5050"]
