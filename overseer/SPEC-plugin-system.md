# Plugin System Enhancement Specification

## Overview
Add a plugin registry system to Overseer that allows environments to specify their dependencies and requirements through a manifest file. The system will store these manifests in a database and use them during deployment.

## Database Changes

Add new table for plugin registry and modify existing deployments table:

```sql
-- Plugin Registry Table
CREATE TABLE plugins (
    id VARCHAR(24) PRIMARY KEY,  -- CUID2 ID (24 chars)
    name VARCHAR(255) NOT NULL UNIQUE,
    version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    manifest TEXT NOT NULL,  -- Store as readable YAML text
    image_name VARCHAR(255) NOT NULL,
    registry_url VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true
);

-- Add plugin reference to deployments
ALTER TABLE deployments 
ADD COLUMN plugin_id VARCHAR(24) REFERENCES plugins(id);
```

## Plugin Manifest Schema

Example manifest for the Claude environment:

```yaml
name: claude-environment
version: 1.0.0
image:
  name: a8s-claude
  registry: local
  pull_policy: Never
dependencies:
  env_vars:
    required:
      - name: ANTHROPIC_API_KEY
        description: API key for Anthropic services
    optional:
      - name: HEIGHT
        description: Display height
        default: "768"
      - name: WIDTH
        description: Display width
        default: "1024"
      - name: DISPLAY_NUM
        description: X display number
        default: "1"
  volumes:
    - name: github-credentials
      mount_path: /home/computeruse/.github-credentials
      type: secret
  resources:
    cpu:
      min: "1"
      max: "2"
    memory:
      min: "2Gi"
      max: "4Gi"
ports:
  - name: vnc
    container_port: 5900
  - name: streamlit
    container_port: 8501
  - name: novnc
    container_port: 6080
  - name: api
    container_port: 8080
ingress:
  enabled: true
  paths:
    - path: /streamlit
      service_port: streamlit
    - path: /novnc
      service_port: novnc
    - path: /api
      service_port: api
```

## Implementation Details

### 0. Database Setup

```yaml
# k8s/postgres.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
  namespace: a8s
data:
  POSTGRES_DB: overseer
  POSTGRES_USER: overseer
  POSTGRES_PASSWORD: overseer  # For production, use proper secrets management

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: a8s
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: a8s-storage
  resources:
    requests:
      storage: 1Gi

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: a8s
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:14
          envFrom:
            - configMapRef:
                name: postgres-config
          ports:
            - containerPort: 5432
          volumeMounts:
            - mountPath: /var/lib/postgresql/data
              name: postgres-data
      volumes:
        - name: postgres-data
          persistentVolumeClaim:
            claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: a8s
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
  type: ClusterIP
```

```python
# overseer/db/database.py
from databases import Database
from sqlalchemy import create_engine, MetaData
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://overseer:overseer@postgres:5432/overseer"
)

# For SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# For async operations
database = Database(DATABASE_URL)

async def get_database() -> Database:
    await database.connect()
    return database
```

```python
# overseer/db/migrations/001_initial.py
from yoyo import step

steps = [
    step(
        """
        CREATE TABLE plugins (
            id VARCHAR(24) PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            version VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            manifest TEXT NOT NULL,
            image_name VARCHAR(255) NOT NULL,
            registry_url VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT true
        )
        """,
        "DROP TABLE plugins"
    ),
    step(
        """
        ALTER TABLE deployments 
        ADD COLUMN plugin_id VARCHAR(24) REFERENCES plugins(id)
        """,
        "ALTER TABLE deployments DROP COLUMN plugin_id"
    )
]
```

Update the Overseer deployment to include database configuration:

```yaml
# k8s/overseer.yaml
# Add to existing ConfigMap
data:
  DATABASE_URL: postgresql://overseer:overseer@postgres:5432/overseer

# Add to Deployment spec
spec:
  template:
    spec:
      initContainers:
        - name: wait-for-postgres
          image: busybox
          command: ['sh', '-c', 'until nc -z postgres 5432; do echo waiting for postgres; sleep 2; done;']
      containers:
        - name: overseer
          # ... existing config ...
          envFrom:
            - configMapRef:
                name: overseer-config
```

Update minikube setup script:

```bash
# k8s/setup-minikube.sh
#!/bin/bash
set -e

echo "Setting up minikube for a8s project..."

# [Previous minikube checks remain the same]

# Start minikube with appropriate resources
echo "Starting minikube cluster..."
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable necessary addons
echo "Enabling necessary addons..."
minikube addons enable ingress
minikube addons enable storage-provisioner
minikube addons enable metrics-server

# Create namespace and storage class
echo "Creating namespace and storage class..."
kubectl create namespace a8s --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f storage-class.yaml

# Deploy PostgreSQL
echo "Deploying PostgreSQL..."
kubectl apply -f postgres.yaml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n a8s --timeout=120s

# Build and load Overseer image
echo "Building Overseer image..."
eval $(minikube docker-env)
docker build -t overseer:latest ../overseer

# Run database migrations
echo "Running database migrations..."
kubectl apply -f migrations-job.yaml
kubectl wait --for=condition=complete job/db-migrations -n a8s --timeout=60s

# Deploy Overseer
echo "Deploying Overseer..."
kubectl apply -f overseer.yaml

# Load Claude environment image
echo "Loading Claude environment image..."
minikube image load a8s-claude:latest

echo "Setup complete! Use 'kubectl get pods -n a8s' to check status"
```

### 1. Models

```python
# overseer/models/plugin.py
from datetime import datetime
from typing import Optional
import yaml
from pydantic import BaseModel, Field
from cuid2 import cuid_wrapper

generate_id = cuid_wrapper()

class PluginManifest(BaseModel):
    name: str
    version: str
    image: dict
    dependencies: dict
    ports: list[dict]
    ingress: Optional[dict] = None

class Plugin(BaseModel):
    id: str = Field(default_factory=generate_id)
    name: str
    version: str
    manifest: str  # YAML text
    image_name: str
    registry_url: str
    is_active: bool = True

    @classmethod
    def from_manifest(cls, manifest_yaml: str) -> "Plugin":
        manifest_dict = yaml.safe_load(manifest_yaml)
        return cls(
            name=manifest_dict["name"],
            version=manifest_dict["version"],
            manifest=manifest_yaml,
            image_name=manifest_dict["image"]["name"],
            registry_url=manifest_dict["image"].get("registry", "local")
        )

    def get_manifest(self) -> PluginManifest:
        return PluginManifest(**yaml.safe_load(self.manifest))
```

### 2. API Endpoints

```python
# overseer/api/plugins.py
from fastapi import APIRouter, UploadFile, HTTPException
from ..models.plugin import Plugin
from ..db.database import Database

router = APIRouter(prefix="/plugins", tags=["plugins"])

@router.post("", response_model=Plugin)
async def register_plugin(
    manifest_file: UploadFile,
    db: Database
) -> Plugin:
    """Register a new plugin with the system."""
    manifest_content = await manifest_file.read()
    manifest_text = manifest_content.decode()
    
    try:
        plugin = Plugin.from_manifest(manifest_text)
        
        # Store in database
        query = """
        INSERT INTO plugins (id, name, version, manifest, image_name, registry_url)
        VALUES (:id, :name, :version, :manifest, :image_name, :registry_url)
        RETURNING *
        """
        values = {
            "id": plugin.id,
            "name": plugin.name,
            "version": plugin.version,
            "manifest": manifest_text,
            "image_name": plugin.image_name,
            "registry_url": plugin.registry_url
        }
        result = await db.fetch_one(query, values)
        return Plugin(**result)
        
    except yaml.YAMLError:
        raise HTTPException(400, "Invalid YAML manifest")
    except ValueError as e:
        raise HTTPException(400, str(e))

# Modify existing deployment endpoint in overseer/api/deployments.py
@router.post("/deployments", response_model=DeploymentResponse)
async def create_deployment(
    request: DeploymentRequest,
    db: Database,
    k8s_client: KubernetesClient
) -> DeploymentResponse:
    """Create a new deployment using registered plugin."""
    # Get plugin from registry
    query = "SELECT * FROM plugins WHERE name = :name AND is_active = true"
    plugin_record = await db.fetch_one(query, {"name": request.environment_type})
    
    if not plugin_record:
        raise HTTPException(404, f"Plugin {request.environment_type} not found")
    
    plugin = Plugin(**plugin_record)
    manifest = plugin.get_manifest()
    
    # Validate dependencies from manifest against request
    validate_dependencies(manifest.dependencies, request.data)
    
    # Create deployment with plugin info
    deployment_id, connection_details = await k8s_client.create_deployment(
        plugin=plugin,
        tools=request.tools,
        data=request.data,
        requirement=request.requirement,
        ttl_seconds=request.ttl_seconds
    )
    
    # Store deployment with plugin reference
    query = """
    INSERT INTO deployments (id, plugin_id, deployment_id, status, config)
    VALUES (:id, :plugin_id, :deployment_id, :status, :config)
    RETURNING *
    """
    values = {
        "id": generate_id(),
        "plugin_id": plugin.id,
        "deployment_id": deployment_id,
        "status": "CREATING",
        "config": yaml.dump(request.dict())
    }
    
    deployment_record = await db.fetch_one(query, values)
    return DeploymentResponse(**deployment_record)
```

### 3. Integration Test

```python
# overseer/integration_test.py
import asyncio
import httpx
import yaml
from pathlib import Path
import os

# Configuration
OVERSEER_URL = os.getenv("OVERSEER_URL", "http://localhost:8000")  # Default to localhost for port forwarding

async def wait_for_deployment_ready(client: httpx.AsyncClient, deployment_id: str, timeout: int = 300):
    """Wait for deployment to be ready."""
    start_time = asyncio.get_event_loop().time()
    while True:
        if asyncio.get_event_loop().time() - start_time > timeout:
            raise TimeoutError(f"Deployment {deployment_id} did not become ready within {timeout} seconds")
            
        response = await client.get(f"{OVERSEER_URL}/deployments/{deployment_id}")
        if response.status_code != 200:
            raise Exception(f"Failed to get deployment status: {response.text}")
            
        status = response.json()["status"]
        if status == "READY":
            return
        elif status == "FAILED":
            raise Exception(f"Deployment {deployment_id} failed")
            
        await asyncio.sleep(5)

async def test_plugin_registration_and_deployment():
    """Test the complete plugin registration and deployment flow using Claude environment."""
    # Load Claude environment manifest from file
    manifest_path = Path(__file__).parent.parent / "environments" / "claude" / "plugin.yaml"
    assert manifest_path.exists(), f"Plugin manifest not found at {manifest_path}"
    
    async with httpx.AsyncClient() as client:
        # Step 1: Register plugin through Overseer API
        with open(manifest_path, "rb") as f:
            files = {"manifest_file": ("plugin.yaml", f)}
            response = await client.post(f"{OVERSEER_URL}/plugins", files=files)
            assert response.status_code == 200, f"Failed to register plugin: {response.text}"
            plugin_data = response.json()
            assert plugin_data["name"] == "claude-environment"
        
        # Step 2: Create deployment using registered plugin
        deploy_data = {
            "environment_type": "claude-environment",
            "tools": [],
            "data": {
                "ANTHROPIC_API_KEY": "test-key",
                "HEIGHT": "768",
                "WIDTH": "1024"
            },
            "requirement": "test deployment"
        }
        response = await client.post(f"{OVERSEER_URL}/deployments", json=deploy_data)
        assert response.status_code == 201, f"Failed to create deployment: {response.text}"
        deployment_data = response.json()
        
        # Step 3: Wait for deployment to be ready
        deployment_id = deployment_data["deployment_id"]
        await wait_for_deployment_ready(client, deployment_id)
        
        # Step 4: Verify connection details
        response = await client.get(f"{OVERSEER_URL}/deployments/{deployment_id}/connect")
        assert response.status_code == 200, f"Failed to get connection details: {response.text}"
        connection = response.json()
        assert "novnc_port" in connection["connection_details"]
        
        # Step 5: Clean up - delete deployment
        response = await client.delete(f"{OVERSEER_URL}/deployments/{deployment_id}")
        assert response.status_code == 200, f"Failed to delete deployment: {response.text}"

async def test_plugin_validation():
    """Test plugin validation through Overseer API."""
    async with httpx.AsyncClient() as client:
        # Test case 1: Missing required env var
        deploy_data = {
            "environment_type": "claude-environment",
            "tools": [],
            "data": {
                # Missing ANTHROPIC_API_KEY
                "HEIGHT": "768",
                "WIDTH": "1024"
            },
            "requirement": "test deployment"
        }
        response = await client.post(f"{OVERSEER_URL}/deployments", json=deploy_data)
        assert response.status_code == 400
        assert "ANTHROPIC_API_KEY" in response.text.lower()

        # Test case 2: Invalid plugin name
        deploy_data["environment_type"] = "non-existent-plugin"
        response = await client.post(f"{OVERSEER_URL}/deployments", json=deploy_data)
        assert response.status_code == 404

if __name__ == "__main__":
    asyncio.run(test_plugin_registration_and_deployment())
    asyncio.run(test_plugin_validation())
```

To run the tests:
```bash
# overseer/run_integration_tests.sh
#!/bin/bash
set -e

# Change to the script directory
cd "$(dirname "$0")"

# Start port forwarding in the background
echo "Setting up port forwarding..."
kubectl port-forward -n a8s svc/overseer 8000:8000 &
PF_PID=$!

# Give port forwarding a moment to establish
sleep 2

# Run integration tests
echo "Running integration tests..."
PYTHONPATH=. python -m pytest integration_test.py -v --capture=no

# Clean up port forwarding
echo "Cleaning up port forwarding..."
kill $PF_PID
```

The integration tests now:
1. Run outside the cluster and connect to Overseer through port forwarding
2. Use localhost:8000 as the default URL (configurable via OVERSEER_URL env var)
3. Test the complete flow from plugin registration to deployment
4. Include validation test cases
5. Clean up resources after tests

The test script:
1. Sets up port forwarding to the Overseer service
2. Runs the tests against the port-forwarded URL
3. Cleans up the port forwarding when done

## Migration Plan

1. Create new plugins table
2. Add plugin_id column to deployments table (nullable initially)
3. Register existing Claude environment as first plugin
4. Update deployment code to use plugin system
5. Backfill plugin_id for existing deployments

## Testing Strategy

1. Run existing integration tests to ensure backward compatibility
2. Add new plugin registration test using Claude environment
3. Test deployment flow with registered plugin
4. Verify all plugin dependencies are correctly injected
5. Test error cases (missing required env vars, invalid manifests)

## Implementation Steps

1. **Database Setup and Migration (Step 0)**
   - Add PostgreSQL Kubernetes manifests
   - Update Overseer deployment with database config
   - Create database connection module
   - Implement migration system
   - Update minikube setup to deploy database

2. **Plugin Models and Validation**
   - Implement plugin models with Pydantic
   - Add manifest validation
   - Add dependency validation

3. **Plugin Registration API**
   - Add plugin registration endpoint
   - Implement database operations
   - Add error handling

4. **Modify Deployment Logic**
   - Update deployment creation to use plugins
   - Add dependency injection from manifest
   - Update Kubernetes client

5. **Integration Tests**
   - Add database fixtures
   - Add plugin registration tests
   - Update deployment tests
   - Add cleanup procedures

6. **Documentation**
   - Update API documentation
   - Add database setup instructions
   - Add plugin creation guide

## Dependencies

- cuid2 for ID generation
- PyYAML for manifest parsing
- databases[postgresql] for async database operations
- yoyo-migrations for database migrations
- psycopg2-binary for PostgreSQL support
- Existing Claude environment image (a8s-claude:latest)

## Development Workflow

1. Local Development:
   ```bash
   # Start minikube and set up the environment
   cd k8s
   ./setup-minikube.sh
   
   # This will:
   # 1. Start minikube
   # 2. Deploy PostgreSQL with persistent storage
   # 3. Run database migrations using a Kubernetes job
   # 4. Deploy Overseer with database configuration
   # 5. Load the Claude environment image
   ```

Add new files for database setup:

```yaml
# k8s/migrations-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrations
  namespace: a8s
spec:
  template:
    spec:
      containers:
      - name: migrations
        image: overseer:latest  # Uses the same image as Overseer
        command: ["yoyo", "apply", "--database", "postgresql://overseer:overseer@postgres:5432/overseer"]
        envFrom:
          - configMapRef:
              name: postgres-config
      restartPolicy: Never
  backoffLimit: 4
```

Update the minikube setup script:

```bash
# k8s/setup-minikube.sh
#!/bin/bash
set -e

echo "Setting up minikube for a8s project..."

# [Previous minikube checks remain the same]

# Start minikube with appropriate resources
echo "Starting minikube cluster..."
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable necessary addons
echo "Enabling necessary addons..."
minikube addons enable ingress
minikube addons enable storage-provisioner
minikube addons enable metrics-server

# Create namespace and storage class
echo "Creating namespace and storage class..."
kubectl create namespace a8s --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f storage-class.yaml

# Deploy PostgreSQL
echo "Deploying PostgreSQL..."
kubectl apply -f postgres.yaml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n a8s --timeout=120s

# Build and load Overseer image
echo "Building Overseer image..."
eval $(minikube docker-env)
docker build -t overseer:latest ../overseer

# Run database migrations
echo "Running database migrations..."
kubectl apply -f migrations-job.yaml
kubectl wait --for=condition=complete job/db-migrations -n a8s --timeout=60s

# Deploy Overseer
echo "Deploying Overseer..."
kubectl apply -f overseer.yaml

# Load Claude environment image
echo "Loading Claude environment image..."
minikube image load a8s-claude:latest

echo "Setup complete! Use 'kubectl get pods -n a8s' to check status"
```

Update integration test script:

```bash
# overseer/run_integration_tests.sh
#!/bin/bash
set -e

# Change to the script directory
cd "$(dirname "$0")"

# Start port forwarding in the background
echo "Setting up port forwarding..."
kubectl port-forward -n a8s svc/overseer 8000:8000 &
PF_PID=$!

# Give port forwarding a moment to establish
sleep 2

# Run integration tests
echo "Running integration tests..."
PYTHONPATH=. python -m pytest integration_test.py -v --capture=no

# Clean up port forwarding
echo "Cleaning up port forwarding..."
kill $PF_PID
```

The key changes:
1. Everything runs inside minikube - no port forwarding needed
2. Database migrations run as a Kubernetes job
3. Integration tests use in-cluster database URL
4. All services communicate through Kubernetes service discovery

This setup ensures:
1. Consistent environment between development and testing
2. Proper service discovery and networking
3. Automated database setup and migrations
4. Clean development workflow 