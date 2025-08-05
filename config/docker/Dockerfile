FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Slither
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    solc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Install the package
RUN pip install -e .

# Expose the API port
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
