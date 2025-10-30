FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install uv && uv install

# Create the directory for rembg models
RUN mkdir -p /root/.u2net/

# Download the u2net.onnx model
RUN wget -q https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx -O /root/.u2net/u2net.onnx


FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /root/.u2net/ /root/.u2net/
COPY app.py .

EXPOSE 8090

# Run with Gunicorn for production
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:8090"]
