# Kubernetes Setup for a8s

This directory contains scripts and configuration files for setting up the Kubernetes infrastructure for the a8s project.

## Prerequisites

- [minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Docker](https://docs.docker.com/get-docker/)
- Local Docker image `a8s-claude:latest`
- Anthropic API key

## Setup Instructions

1. **Build the local Docker image**:

   ```bash
   ./build-local-image.sh
   ```

   This script will build the Docker image `a8s-claude:latest` from the Dockerfile in the `../environments/claude/` directory.

2. **Start minikube and set up the infrastructure**:

   ```bash
   ./setup-minikube.sh
   ```

   This script will:
   - Start minikube with appropriate resources
   - Load the local Docker image `a8s-claude:latest` into minikube
   - Enable necessary addons (ingress, storage-provisioner, metrics-server)
   - Create the a8s namespace
   - Set up a basic storage class

3. **Create the Anthropic API key secret**:

   ```bash
   export ANTHROPIC_API_KEY=your_api_key
   ./create-secret.sh
   ```

4. **Deploy the Claude environment**:

   ```bash
   kubectl apply -f claude-deployment.yaml
   ```

5. **Check the deployment status**:

   ```bash
   kubectl get pods -n a8s
   kubectl get services -n a8s
   kubectl get ingress -n a8s
   ```

6. **Access the services**:

   To access the services, you need to get the minikube IP:

   ```bash
   minikube ip
   ```

   Then, you can access the services at:
   - Streamlit: http://<minikube-ip>/streamlit
   - noVNC: http://<minikube-ip>/novnc
   - API: http://<minikube-ip>/api

   Alternatively, you can use port forwarding:

   ```bash
   kubectl port-forward service/claude-environment-service 8501:8501 6080:6080 8080:8080 -n a8s
   ```

   Then access:
   - Streamlit: http://localhost:8501
   - noVNC: http://localhost:6080
   - API: http://localhost:8080

## Cleanup

To clean up the resources:

```bash
kubectl delete -f claude-deployment.yaml
minikube stop
```

To completely delete the minikube cluster:

```bash
minikube delete
``` 