FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the environment and inference script
COPY my_env/ /app/my_env/
COPY inference.py /app/
COPY openenv.yaml /app/

# The HF Space will ping the /reset endpoint, so OpenEnv-core handles the server.
# By default, openenv runs on port 8000
EXPOSE 8000

CMD ["openenv", "serve", "--host", "0.0.0.0", "--port", "8000"]