# ---------- Base Image ----------
FROM python:3.11-slim

# ---------- Environment Setup ----------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# ---------- System Dependencies ----------
# Install Java (OpenJDK 17) + gcc/g++ for C/C++ checks
RUN apt-get update -y && \
    apt-get install -y openjdk-17-jdk gcc g++ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ---------- Copy Project Files ----------
COPY requirements.txt ./

# ---------- Install Python Packages ----------
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy App Source ----------
COPY . .

# ---------- Expose Port ----------
EXPOSE 8080

# ---------- Run Flask via Gunicorn ----------
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
