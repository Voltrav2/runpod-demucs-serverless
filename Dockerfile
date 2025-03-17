# Resmi Python slim imajını kullan
FROM python:3.10-slim

# Çalışma dizinini belirle
WORKDIR /app

# Gerekli paketleri yükle
RUN pip install --no-cache-dir runpod demucs torch numpy wget

# Kod dosyalarını kopyala
COPY rp_handler.py /app/rp_handler.py

# Serverless worker başlat
CMD ["python3", "-u", "/app/rp_handler.py"]
