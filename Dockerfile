FROM python:3.11-slim

# ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg ca-certificates tzdata && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py entrypoint.sh urls.txt ./

# 运行目录：数据与归档
VOLUME ["/data", "/secrets"]
ENTRYPOINT ["/app/entrypoint.sh"]
