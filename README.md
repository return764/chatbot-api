docker run -d \
  --name chatbot \
  -p 5140:5140 \
  -v $(pwd)/config.toml:/app/config.toml \
  -v $(pwd)/.data:/app/.data \
  chatbot