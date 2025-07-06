# Use official Python 3.10 image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies required by OpenCV
RUN apt-get update && \
    apt-get install -y \
        libgl1 \
        libsm6 \
        ffmpeg \
        libglib2.0-0 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first
COPY backend/requirements.txt .

# DEBUG: Show contents of requirements.txt
RUN cat requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy .env file into the container
COPY .env /app/.env

# Copy FastAPI app code
COPY backend/app ./app/

# Copy models folder
COPY backend/models ./models/

# Expose FastAPI port
EXPOSE 8000

# Run Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]