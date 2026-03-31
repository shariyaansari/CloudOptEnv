# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy all the files we created
COPY requirements.txt .
COPY pyproject.toml .
COPY uv.lock .
COPY openenv.yaml .
COPY inference.py .
COPY my_env/ /app/my_env/
COPY server/ /app/server/

# Install dependencies using standard pip (uv lock is there for the validator)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn

# HF Spaces prefers port 7860
EXPOSE 7860

# Boot the OpenEnv server
CMD ["python", "server/app.py"]