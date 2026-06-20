FROM mongo:7

# Install required tools for data loading
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Copy initialization script
COPY init-mongodb.js /docker-entrypoint-initdb.d/01-init-schema.js

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy data loading script
COPY load_data.py .

# Copy raw data
COPY ../etl/data/raw /app/data/raw

# Expose MongoDB port
EXPOSE 27017

CMD ["mongod", "--auth"]
