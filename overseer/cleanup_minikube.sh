#!/bin/bash
set -e

# Change to the script directory
cd "$(dirname "$0")"

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "Error: Minikube is not running. Cleanup may be incomplete."
    exit 1
fi

# Stop port forwarding if it's running
if [ -f .port_forward_pid ]; then
    PORT_FORWARD_PID=$(cat .port_forward_pid)
    if ps -p $PORT_FORWARD_PID > /dev/null; then
        echo "Stopping port forwarding (PID: $PORT_FORWARD_PID)..."
        kill $PORT_FORWARD_PID || true
    fi
    rm .port_forward_pid
fi

# Delete the Overseer deployment and related resources
echo "Deleting Overseer deployment and related resources from Minikube..."
kubectl delete -f k8s/overseer.yaml --ignore-not-found=true

# Optionally, delete the namespace (uncomment if you want to delete the namespace)
# echo "Deleting a8s namespace..."
kubectl delete namespace a8s --ignore-not-found=true

echo "Cleanup completed." 