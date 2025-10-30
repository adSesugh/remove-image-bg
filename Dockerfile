FROM python:3.12-slim as base

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*


COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install uv
RUN uv sync

# Create the directory for rembg models
RUN mkdir -p /root/.u2net/

# Download the u2net.onnx model
RUN wget -q https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx -O /root/.u2net/u2net.onnx


FROM python:3.12-slim as builder

WORKDIR /app

# Copy only necessary files from the builder stage
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /root/.u2net/ /root/.u2net/
COPY --from=base app.py .

EXPOSE 8090

# Run with Gunicorn for production
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:8090"]
