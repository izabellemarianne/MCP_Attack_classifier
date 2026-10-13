FROM python:3.11-slim
FROM python:3.11-slim

WORKDIR /app

# CPU-only torch keeps the image small
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY serving/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/download_models.py scripts/download_models.py
RUN --mount=type=secret,id=hf_token,required=true \
    echo "token file size: $(wc -c < /run/secrets/hf_token) bytes" && \
    test -s /run/secrets/hf_token && \
    HF_TOKEN=$(cat /run/secrets/hf_token) python scripts/download_models.py

# From here on, use only the cached copies and don't call the Hub at runtime
ENV HF_HUB_OFFLINE=1

COPY . .

EXPOSE 8000
CMD ["uvicorn", "serving.deploy:app", "--host", "0.0.0.0", "--port", "8000"]