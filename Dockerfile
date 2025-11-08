# ------------------ Base Image ------------------
FROM openjdk:17-jdk-slim

# ------------------ Install Required Tools ------------------
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-venv gcc g++ curl npm git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------ Install Node.js ------------------
RUN npm install -g n && \
    n stable && \
    ln -sf /usr/local/bin/node /usr/bin/node && \
    ln -sf /usr/local/bin/npm /usr/bin/npm

# ------------------ Set Working Directory ------------------
WORKDIR /app

# ------------------ Copy Project Files ------------------
COPY . /app

# ------------------ Install Python Dependencies ------------------
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install flask flask-cors beautifulsoup4 gunicorn

# ------------------ Expose Port ------------------
EXPOSE 1000

# ------------------ Environment Variables ------------------
ENV PORT=1000
ENV PYTHONUNBUFFERED=1

# ------------------ Start Flask App ------------------
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:1000", "--workers", "1"]
