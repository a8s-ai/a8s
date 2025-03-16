# Overseer

Kubernetes deployment service for the a8s project.

## Overview

Overseer is a FastAPI-based service that manages deployments of AI agent environments in Kubernetes. It provides a simple API for creating, monitoring, and connecting to these environments.

## Features

- Create deployments with specific environment types, tools, and requirements
- Monitor deployment status
- Get connection details for running deployments
- Delete deployments when they are no longer needed

## Requirements

- Python 3.11+
- Kubernetes cluster (or minikube for local development)
- Docker (for building the container image)
- uv (for dependency management)

## Installation

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/yourusername/a8s.git
cd a8s/overseer
```

2. Install dependencies using uv:

```bash
# Install base dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"

# Install test dependencies
uv pip install -e ".[test]"
```

3. Run the service:

```bash
python run.py
```

### Docker

1. Build the Docker image:

```bash
docker build -t overseer:latest .
```

The Dockerfile:
- Uses Python 3.12 slim as the base image
- Copies all application code to the container
- Installs the package in development mode
- Exposes port 8000
- Runs the application using `python run.py`

2. Run the container:

```bash
docker run -p 8000:8000 overseer:latest
```

### Docker Compose

You can also use Docker Compose to run the service:

```bash
docker-compose up
```

This will build the image and start the service with the appropriate volumes mounted for accessing minikube.

## Integration Tests

To run the integration tests, you need to have minikube running and uv installed:

```bash
# Start minikube if it's not already running
minikube start

# Run the integration tests
./run_integration_tests.sh
```

The integration tests will:
1. Check if minikube is running
2. Install the Overseer package with test dependencies using uv
3. Deploy the Overseer service to Minikube (rather than running it locally)
4. Run tests against the API endpoints
5. Clean up resources

This approach ensures that Overseer runs in the same environment where it will deploy agent environments, providing a more realistic test scenario.

## API Endpoints

The API documentation is available at `/docs` when the service is running. Here's a summary of the available endpoints:

- `POST /deployments`: Create a new deployment
- `GET /deployments/{deployment_id}`: Get deployment details
- `GET /deployments/{deployment_id}/status`: Get deployment status
- `GET /deployments/{deployment_id}/connect`: Get connection details
- `DELETE /deployments/{deployment_id}`: Delete a deployment

## Environment Variables

The service can be configured using the following environment variables:

- `OVERSEER_HOST`: Host to bind to (default: 0.0.0.0)
- `OVERSEER_PORT`: Port to bind to (default: 8000)
- `OVERSEER_RELOAD`: Enable auto-reload (default: False)
- `OVERSEER_WORKERS`: Number of worker processes (default: 1)
- `OVERSEER_LOG_LEVEL`: Log level (default: info)

## Example Usage

### Create a Deployment

```bash
curl -X POST "http://localhost:8000/deployments" \
  -H "Content-Type: application/json" \
  -d '{
    "environment_type": "claude",
    "tools": ["web-search", "code-interpreter"],
    "data": {
      "context": "This is some context for the agent"
    },
    "requirement": "Analyze the provided data and generate insights"
  }'
```

### Get Deployment Status

```bash
curl -X GET "http://localhost:8000/deployments/{deployment_id}/status"
```

### Get Connection Details

```bash
curl -X GET "http://localhost:8000/deployments/{deployment_id}/connect"
```

### Delete a Deployment

```bash
curl -X DELETE "http://localhost:8000/deployments/{deployment_id}"
```

## License

[MIT License](LICENSE)
