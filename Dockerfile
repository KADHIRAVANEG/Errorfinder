# ------------------ Base Image ------------------
FROM openjdk:17-slim

# ------------------ Install Required Tools ------------------
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-venv gcc g++ curl npm git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------ Install Node.js for JavaScript Execution ------------------
RUN npm install -g n && \
    n stable && \
    ln -sf /usr/local/bin/node /usr/bin/node && \
    ln -sf /usr/local/bin/npm /usr/bin/npm

# ------------------ Set Working Directory ------------------
WORKDIR /app

# ------------------ Copy Project Files ------------------
COPY . /app

# ------------------ Install Python Dependencies ------------------
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# ------------------ Expose Port ------------------
EXPOSE 1000

# ------------------ Environment Variables ------------------
ENV PORT=1000
ENV PYTHONUNBUFFERED=1

# ------------------ Start the Flask App ------------------
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT --workers 1"]
