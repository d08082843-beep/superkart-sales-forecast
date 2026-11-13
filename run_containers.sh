#!/bin/bash
set -e

# Create a Docker network so that the two containers can talk to each other
docker network create superkart-net 2>/dev/null || true

# Build the backend and frontend images
docker build -t superkart-backend ./backend_files
docker build -t superkart-frontend ./frontend_files

# Remove old containers if they exist (makes the script safe to re-run)
docker rm -f superkart-backend superkart-frontend 2>/dev/null || true

# Start the Flask backend on port 7860
docker run -d --name superkart-backend --network superkart-net -p 7860:7860 superkart-backend

# Start the Streamlit frontend on port 8501, pointing it to the backend container
docker run -d --name superkart-frontend --network superkart-net -p 8501:8501 \
    -e BACKEND_URL=http://superkart-backend:7860 superkart-frontend

docker ps
echo "Backend:  port 7860  |  Frontend: port 8501"
