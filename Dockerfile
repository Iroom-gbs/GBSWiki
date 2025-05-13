FROM python:3.10-slim

# Set environment variable inside container
ENV NAMU_DB_TYPE sqlite
ENV NAMU_DB data
ENV NAMU_HOST 0.0.0.0
ENV NAMU_PORT 8000
ENV NAMU_LANG ko-KR
ENV NAMU_MARKUP namumark
ENV NAMU_ENCRYPT sha3
# Set Google OAuth credentials
ENV GOOGLE_CLIENT_ID="YOUR_CLIENT_ID"
ENV GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET"
# Install git
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Set base working directory
WORKDIR /app

# Clone the repository into /app/GBSWiki
RUN git clone https://github.com/Iroom-gbs/GBSWiki.git /app/GBSWiki

# Change to repository directory
WORKDIR /app/GBSWiki

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "app.py"]
