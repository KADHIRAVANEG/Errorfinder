# ------------------ Base Image ------------------
FROM openjdk:17-slim

# ------------------ Install Python + Build Tools ------------------
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-venv gcc g++ && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------ Set Working Directory ------------------
WORKDIR /app

# ------------------ Copy Project Files ------------------
COPY . /app

# ------------------ Install Python Dependencies ------------------
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# ------------------ Environment Variables ------------------
ENV PORT 8080

# ------------------ Start the Flask App ------------------
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080"]
