# Kubernetes Setup for a8s

This directory contains scripts and configuration files for setting up the Kubernetes infrastructure for the a8s project.

## Prerequisites

- [minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Docker](https://docs.docker.com/get-docker/)
- Anthropic API key

## Setup Instructions

1. **Prepare environment**:
   ```bash
   # Create empty GitHub credentials file (required for Claude environment)
   touch environments/claude/.github-credentials
   ```

2. **Build the local Docker image**:

   ```bash
   ./build-local-image.sh
   ```

   This script will build:
   - `a8s-claude:latest` from the Dockerfile in `../environments/claude/`
   - `a8s-web:latest` from the Dockerfile in `../web/`

3. **Start minikube and set up the infrastructure**:

   ```bash
   ./setup-minikube.sh
   ```

   This script will:
   - Start minikube with appropriate resources
   - Load both Docker images into minikube
   - Enable necessary addons (ingress, storage-provisioner, metrics-server)
   - Create the a8s namespace
   - Set up a basic storage class

4. **Create secrets and configuration**:

   ```bash
   # Set up your Anthropic API key
   export ANTHROPIC_API_KEY=your_api_key

   # Optional: Create .env.production for web application secrets
   # Copy your web environment variables to ../web/.env.production

   # Create secrets and config maps
   ./create-secret.sh
   ```

5. **Deploy the applications**:

   ```bash
   # Deploy the Claude environment
   kubectl apply -f claude-deployment.yaml

   # Deploy the web application
   kubectl apply -f web-deployment.yaml
   ```

6. **Check the deployment status**:

   ```bash
   kubectl get pods -n a8s
   kubectl get services -n a8s
   kubectl get ingress -n a8s
   ```

7. **Access the services**:

   To access the services, you need to get the minikube IP:

   ```bash
   minikube ip
   ```

   Then, you can access the services at:
   - Web App: http://<minikube-ip>/
   - Streamlit: http://<minikube-ip>/streamlit
   - noVNC: http://<minikube-ip>/novnc
   - API: http://<minikube-ip>/api

   Alternatively, you can use port forwarding:

   ```bash
   # For web application
   kubectl port-forward service/web-service 3000:3000 -n a8s

   # For Claude environment
   kubectl port-forward service/claude-environment-service 8501:8501 6080:6080 8080:8080 -n a8s
   ```

   Then access:
   - Web App: http://localhost:3000
   - Streamlit: http://localhost:8501
   - noVNC: http://localhost:6080
   - API: http://localhost:8080

## Development Workflow

When making changes to the applications:

1. Make your changes in the respective directories (`web/` or `environments/claude/`)
2. Rebuild the Docker images:
   ```bash
   ./build-local-image.sh
   ```
3. Load the new images into minikube:
   ```bash
   minikube image load a8s-web:latest
   minikube image load a8s-claude:latest
   ```
4. Restart the deployments:
   ```bash
   kubectl rollout restart deployment web-deployment -n a8s
   kubectl rollout restart deployment claude-deployment -n a8s
   ```

## Cleanup

To clean up the resources:

```bash
kubectl delete -f web-deployment.yaml
kubectl delete -f claude-deployment.yaml
minikube stop
```

To completely delete the minikube cluster:

```bash
minikube delete
``` 