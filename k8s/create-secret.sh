#!/bin/bash
set -e

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable is not set."
    echo "Please set it with: export ANTHROPIC_API_KEY=your_api_key"
    exit 1
fi

# Create the secret
echo "Creating Anthropic API key secret..."
kubectl create secret generic anthropic-credentials \
    --from-literal=api-key="$ANTHROPIC_API_KEY" \
    --namespace=a8s \
    --dry-run=client -o yaml | kubectl apply -f -

echo "Secret created successfully!" 