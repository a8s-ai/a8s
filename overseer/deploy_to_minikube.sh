#!/bin/bash
set -e

# Change to the script directory
cd "$(dirname "$0")"

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "Error: Minikube is not running. Please start Minikube before deploying."
    echo "You can start Minikube with: minikube start"
    exit 1
fi

# Create the k8s directory if it doesn't exist
mkdir -p k8s

# Set docker to use minikube's docker daemon
echo "Setting up Docker environment to use Minikube's Docker daemon..."
eval $(minikube docker-env)

# Build the Docker image
echo "Building Overseer Docker image..."
docker build -t overseer:latest .

# Create the namespace if it doesn't exist
echo "Creating namespace if it doesn't exist..."
kubectl create namespace a8s --dry-run=client -o yaml | kubectl apply -f -

# Apply the Kubernetes manifests
echo "Deploying Overseer to Minikube..."
kubectl apply -f k8s/overseer.yaml

# Wait for the deployment to be ready
echo "Waiting for Overseer deployment to be ready..."
kubectl -n a8s rollout status deployment/overseer

# Get the service URL
echo "Setting up port forwarding for Overseer service..."
# Use nohup to ensure the port forwarding continues even if the script exits
nohup kubectl -n a8s port-forward svc/overseer 8000:8000 > /dev/null 2>&1 &
PORT_FORWARD_PID=$!

# Give the port forwarding a moment to establish
sleep 3

# Check if port forwarding is actually running
if ! ps -p $PORT_FORWARD_PID > /dev/null; then
    echo "Error: Port forwarding failed to start"
    exit 1
fi

echo "Overseer is now deployed and accessible at http://localhost:8000"
echo "Port forwarding is running with PID: $PORT_FORWARD_PID"
echo "To stop port forwarding, run: kill $PORT_FORWARD_PID"

# Save the port forwarding PID to a file for later cleanup
echo $PORT_FORWARD_PID > .port_forward_pid

# Exit the script
exit 0 