#!/bin/sh
set -e

/bin/ollama serve &
pid=$!

while ! curl -s http://localhost:11434 > /dev/null; do
    echo "Waiting for Ollama server to start..."
    sleep 1
done

# Pull models listed in MODELS_TO_PULL (space-separated)
for model_name in $MODELS_TO_PULL; do
    echo " ------------- Pulling model: ${model_name} ------------- "
    ollama pull "${model_name}"
done

# Stop the temporary server
kill $pid
wait $pid

# Start the main Ollama server
echo "Starting main Ollama server (llm server ready h)"
exec /bin/ollama serve
