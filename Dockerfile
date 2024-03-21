# Use Python 3.10 with Debian (slim version)
FROM python:3.10-slim

# Create required directory structure
RUN mkdir -p /home/automa/chat.automa.one

# Set working directory
WORKDIR /home/automa/chat.automa.one

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl dpkg sudo && \
    curl -L --output /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && \
    dpkg -i /tmp/cloudflared.deb && \
    cloudflared service install eyJhIjoiNzJlYjBmNzlmNjQ2ZjBiMmVjMmMwODQyMzc4NDc0NjIiLCJ0IjoiNjUwZGM5ZDAtZDJjNC00ZmYwLTk0NGItYWJkOTE4ODUwOTFiIiwicyI6Ik4ySTRPR05qWldZdFkyVTRNUzAwWmpFeUxXSXpaRGd0T0RKbVpqWTNZelkyTVRrMCJ9 && \
    rm /tmp/cloudflared.deb

# Copy the entire directory into the container
COPY . /home/automa/chat.automa.one

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run Gunicorn when the container launches
CMD sudo cloudflared service uninstall && \
sudo cloudflared service install eyJhIjoiNzJlYjBmNzlmNjQ2ZjBiMmVjMmMwODQyMzc4NDc0NjIiLCJ0IjoiNjUwZGM5ZDAtZDJjNC00ZmYwLTk0NGItYWJkOTE4ODUwOTFiIiwicyI6Ik4ySTRPR05qWldZdFkyVTRNUzAwWmpFeUxXSXpaRGd0T0RKbVpqWTNZelkyTVRrMCJ9 && \
gunicorn -w 4 --timeout 180 wsgi:application --bind 0.0.0.0:8000