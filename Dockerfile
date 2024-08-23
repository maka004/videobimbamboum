# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# FFmpeg installation with a single RUN command to reduce layers
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app
WORKDIR /app

# Add the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies, including Flask, flask-cors, and others
RUN pip install --no-cache-dir -r requirements.txt

# Add the current directory files to /app in the container
COPY . .

# Run app.py (Flask server) when the container launches
CMD gunicorn --bind 0.0.0.0:$PORT app:app

