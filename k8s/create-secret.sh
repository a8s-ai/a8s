#!/bin/bash
set -e

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable is not set."
    echo "Please set it with: export ANTHROPIC_API_KEY=your_api_key"
    exit 1
fi

# Create the Claude secret
echo "Creating Anthropic API key secret..."
kubectl create secret generic anthropic-credentials \
    --from-literal=api-key="$ANTHROPIC_API_KEY" \
    --namespace=a8s \
    --dry-run=client -o yaml | kubectl apply -f -

# Create web application config map for non-sensitive environment variables
echo "Creating web application config map..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
  namespace: a8s
data:
  NODE_ENV: "production"
  PORT: "3000"
  HOSTNAME: "0.0.0.0"
EOF

# Create web application secrets for sensitive environment variables
# Add any sensitive environment variables your web app needs
if [ -f "../web/.env.production" ]; then
    echo "Creating web application secrets from .env.production file..."
    kubectl create secret generic web-secrets \
        --from-env-file=../web/.env.production \
        --namespace=a8s \
        --dry-run=client -o yaml | kubectl apply -f -
else
    echo "Warning: ../web/.env.production file not found. Skipping web secrets creation."
    echo "If your web application needs environment variables, please create a .env.production file."
fi

echo "Secrets and config maps created successfully!"