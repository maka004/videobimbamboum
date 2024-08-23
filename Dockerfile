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

# Copy all project files to the working directory
COPY . .

# Install Python dependencies directly in Dockerfile
RUN pip install --no-cache-dir flask werkzeug ffmpeg-python requests gunicorn moviepy pydub scipy flask-cors

# Run app.py (Flask server) when the container launches
CMD gunicorn --bind 0.0.0.0:$PORT app:app
