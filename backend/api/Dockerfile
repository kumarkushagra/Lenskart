FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn requests gradio ollama pydantic supabase "websockets>=11.0"

# Copy code
COPY . /app

# Expose ports (8000 for backend, 7860 for frontend)
EXPOSE 8000
EXPOSE 7860

# Default command (can be overridden)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
