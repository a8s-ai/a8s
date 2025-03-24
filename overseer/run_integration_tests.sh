#!/bin/bash
# Run integration tests for the Overseer service

set -e

# Change to the script directory
cd "$(dirname "$0")"

# Function to check minikube status
check_minikube() {
    echo "Checking minikube status..."
    if ! minikube status &> /dev/null; then
        echo "Error: Minikube is not running. Starting minikube..."
        minikube start
    fi
}

# Function to check required tools
check_dependencies() {
    local missing_deps=0
    
    echo "Checking dependencies..."
    for cmd in uv docker minikube kubectl python3; do
        if ! command -v $cmd &> /dev/null; then
            echo "❌ $cmd is not installed"
            missing_deps=1
        else
            echo "✓ $cmd is installed"
        fi
    done
    
    if [ $missing_deps -eq 1 ]; then
        exit 1
    fi
}

# Check dependencies
check_dependencies

# Check minikube status
check_minikube

# Verify kubectl context
echo "Verifying kubectl context..."
current_context=$(kubectl config current-context)
if [ "$current_context" != "minikube" ]; then
    echo "Switching kubectl context to minikube..."
    kubectl config use-context minikube
fi

# Install the package with test dependencies
echo "Installing Overseer with test dependencies..."
uv pip install -e ".[test]"

# Make the deployment and cleanup scripts executable
chmod +x deploy_to_minikube.sh cleanup_minikube.sh

# Clean up any existing deployments
echo "Cleaning up existing deployments..."
./cleanup_minikube.sh || true

# Run the integration tests with verbose output
echo "Running integration tests..."
PYTHONPATH=. python -m pytest integration_test.py -v --capture=no

# Store the exit code
exit_code=$?

# Display test results
if [ $exit_code -eq 0 ]; then
    echo "✅ Integration tests passed!"
else
    echo "❌ Integration tests failed!"
    
    # Show pod status and logs if tests failed
    echo "Debugging information:"
    kubectl get pods -n a8s
    for pod in $(kubectl get pods -n a8s -o jsonpath='{.items[*].metadata.name}'); do
        echo "=== Logs for $pod ==="
        kubectl logs -n a8s $pod
    done
fi

exit $exit_code