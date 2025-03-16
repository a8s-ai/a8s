#!/bin/bash
# Run integration tests for the Overseer service

set -e

# Change to the script directory
cd "$(dirname "$0")"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install it first:"
    echo "pip install uv"
    exit 1
fi

# Install the package with test dependencies
echo "Installing Overseer with test dependencies..."
uv pip install -e ".[test]"

# Make the deployment and cleanup scripts executable
chmod +x deploy_to_minikube.sh cleanup_minikube.sh

# Run the integration tests
echo "Running integration tests..."
python integration_test.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo "Integration tests passed!"
    exit 0
else
    echo "Integration tests failed!"
    exit 1
fi 