#!/bin/bash
set -e

echo "Building local Docker images for a8s..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install it first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Check if the Dockerfile exists in the environments/claude directory
if [ ! -f "../environments/claude/Dockerfile" ]; then
    echo "Error: Dockerfile not found in ../environments/claude/"
    echo "Please make sure you're running this script from the k8s directory."
    exit 1
fi

# Check if the Web Dockerfile exists
if [ ! -f "../web/Dockerfile" ]; then
    echo "Error: Dockerfile not found in ../web/"
    echo "Please make sure you're running this script from the k8s directory."
    exit 1
fi

# Build the Claude environment image
echo "Building Docker image 'a8s-claude' from ../environments/claude/Dockerfile..."
docker build -t a8s-claude:latest -f ../environments/claude/Dockerfile ../environments/claude

# Build the web application image
echo "Building Docker image 'a8s-web' from ../web/Dockerfile..."
docker build -t a8s-web:latest -f ../web/Dockerfile ../web

echo "Docker images built successfully!"
echo "You can now run ./setup-minikube.sh to set up the Kubernetes infrastructure." 