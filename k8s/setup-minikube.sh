#!/bin/bash
set -e

echo "Setting up minikube for a8s project..."

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "minikube is not installed. Please install it first."
    echo "Visit https://minikube.sigs.k8s.io/docs/start/ for installation instructions."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed. Please install it first."
    echo "Visit https://kubernetes.io/docs/tasks/tools/install-kubectl/ for installation instructions."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install it first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Check if the local images exist
check_docker_images() {
    local images=("a8s-claude:latest" "overseer:latest")
    for image in "${images[@]}"; do
        if ! docker image inspect "$image" &> /dev/null; then
            echo "Error: Local Docker image '$image' not found."
            echo "Please build the images first using ./build-local.sh"
            exit 1
        fi
    done
}

# Run image check
check_docker_images

# Start minikube with appropriate resources
echo "Starting minikube cluster..."
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Load the local Docker images into minikube
echo "Loading local Docker images into minikube..."
minikube image load a8s-claude:latest
minikube image load overseer:latest

# Enable necessary addons
echo "Enabling necessary addons..."
minikube addons enable ingress
minikube addons enable storage-provisioner
minikube addons enable metrics-server

# Create namespace for our application
echo "Creating a8s namespace..."
kubectl create namespace a8s --dry-run=client -o yaml | kubectl apply -f -

# Set the default namespace for kubectl
kubectl config set-context --current --namespace=a8s

# Create a basic storage class
echo "Creating storage class..."
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: a8s-storage
  namespace: a8s
provisioner: k8s.io/minikube-hostpath
reclaimPolicy: Delete
volumeBindingMode: Immediate
EOF

echo "Minikube setup complete!"
echo "Cluster status:"
minikube status
