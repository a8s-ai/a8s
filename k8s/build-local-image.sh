#!/bin/bash
set -e

echo "Building local Docker images for a8s..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install it first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Build Claude Docker image
build_claude_image() {
    # Check if the Dockerfile exists in the environments/claude directory
    if [ ! -f "../environments/claude/Dockerfile" ]; then
        echo "Error: Dockerfile not found in ../environments/claude/"
        echo "Please make sure you're running this script from the k8s directory."
        return 1
    fi

    echo "Building Docker image 'a8s-claude' from ../environments/claude/Dockerfile..."
    docker build -t a8s-claude:latest -f ../environments/claude/Dockerfile ../environments/claude
    echo "Docker image 'a8s-claude:latest' built successfully!"
}

# Build Overseer Docker image
build_overseer_image() {
    # Check if the Dockerfile exists in the overseer directory
    if [ ! -f "../overseer/Dockerfile" ]; then
        echo "Error: Dockerfile not found in ../overseer/"
        echo "Please make sure the Overseer project directory exists."
        return 1
    fi

    echo "Building Docker image 'overseer' from ../overseer/Dockerfile..."
    pushd ../overseer > /dev/null
    docker build -t overseer:latest .
    popd > /dev/null
    echo "Docker image 'overseer:latest' built successfully!"
}

# Build both images
build_claude_image
build_overseer_image

echo "All Docker images built successfully!"
echo "You can now run ./setup-minikube.sh to set up the Kubernetes infrastructure."