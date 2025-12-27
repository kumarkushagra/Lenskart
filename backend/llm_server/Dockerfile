FROM ollama/ollama:latest

# install curl (needed by entrypoint.sh) and clean apt cache
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*  

# Default models to pull
ENV MODELS_TO_PULL="gemma3:4b"

# Parallel processing config
ENV OLLAMA_NUM_PARALLEL=10

# Copy entrypoint script into the image
COPY entrypoint.sh /entrypoint.sh

# Make it executable
RUN chmod +x /entrypoint.sh

# Use it as entrypoint
ENTRYPOINT ["/entrypoint.sh"]
