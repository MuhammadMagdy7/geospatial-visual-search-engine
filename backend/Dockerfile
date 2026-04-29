FROM python:3.11-slim

WORKDIR /app

# NOTE: We avoid apt-get because of network restrictions in some environments.
# All Python dependencies are installed via pre-built wheels which require no
# system compilation. If you ever need to add a package that requires compilation
# from source, you may need to switch to `python:3.11` (full image) which includes
# build tools, OR install build-essential via apt-get if your network allows it.

# Install Python dependencies
# Use CPU-only torch wheels to keep image small (~700 MB instead of ~3 GB)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        torch==2.2.0 torchvision==0.17.0 \
        --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# Create cache directories for HuggingFace and tile storage
RUN mkdir -p /data/hf_cache /data/cache

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]