# Dockerfile — uygulamayi tasinabilir bir "kutuya" paketliyorum.
# EN: package the app into a portable container.
# Calistirma / run:
#   docker build -t document-extractor .
#   docker run -p 8501:8501 -e GROQ_API_KEY=xxx document-extractor

# 1) temel imaj: hafif bir Python / base image: slim Python
FROM python:3.11-slim

# 2) calisma klasoru / working directory inside the container
WORKDIR /app

# 3) once sadece requirements'i kopyala + kur (Docker cache'i icin daha hizli)
#    EN: copy requirements first and install (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) geri kalan tum kodu kopyala / copy the rest of the code
COPY . .

# 5) Streamlit portu / Streamlit port
EXPOSE 8501

# 6) container acilinca uygulamayi baslat / start the app when the container runs
#    address 0.0.0.0 -> container disindan erisilebilsin diye
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]