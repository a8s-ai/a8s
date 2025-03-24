#!/usr/bin/env python
"""
Integration test for the Overseer service with minikube.

This script:
1. Checks if minikube is running
2. Checks if the namespace exists and creates it if needed
3. Deploys the Overseer service to Minikube
4. Runs integration tests against the API
5. Cleans up resources
"""

import json
import os
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple, Any

import httpx
import pytest
from kubernetes import client, config

# Constants
OVERSEER_HOST = "localhost"
OVERSEER_PORT = 8000
OVERSEER_URL = f"http://{OVERSEER_HOST}:{OVERSEER_PORT}"
NAMESPACE = "a8s"
TEST_TIMEOUT = 300  # seconds
DOCKER_IMAGE_NAME="a8s-claude:latest"


class Colors:
    """Terminal colors for output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_step(message: str) -> None:
    """Print a step message.

    Args:
        message: The message to print.
    """
    print(f"\n{Colors.HEADER}=== {message} ==={Colors.ENDC}")


def print_success(message: str) -> None:
    """Print a success message.

    Args:
        message: The message to print.
    """
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str) -> None:
    """Print an error message.

    Args:
        message: The message to print.
    """
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def run_command(command: List[str], check: bool = True, timeout: int = 60) -> Tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr.

    Args:
        command: The command to run.
        check: Whether to check the exit code.
        timeout: Timeout in seconds for the command to complete.

    Returns:
        A tuple of (exit_code, stdout, stderr).

    Raises:
        subprocess.CalledProcessError: If the command fails and check is True.
        subprocess.TimeoutExpired: If the command times out.
    """
    print(f"Running command: {' '.join(command)}")
    try:
        # Use subprocess.run with timeout instead of Popen
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout
        )
        
        exit_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
        
        if exit_code != 0 and check:
            print_error(f"Command failed with exit code {exit_code}")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            raise subprocess.CalledProcessError(exit_code, command, stdout, stderr)
        
        return exit_code, stdout, stderr
    except subprocess.TimeoutExpired as e:
        print_error(f"Command timed out after {timeout} seconds: {' '.join(command)}")
        return 1, "", f"Command timed out after {timeout} seconds"


def build_and_load_docker_image() -> bool:
    """Build and load the Docker image for the claude environment into Minikube.
    
    Returns:
        True if the image was built and loaded successfully, False otherwise.
    """
    print_step("Building and loading Docker image for claude environment")
    
    try:
        build_script = "../k8s/build-local-image.sh"
        print("Building Docker image...")
        exit_code, stdout, stderr = run_command(build_script, check=True)
        if exit_code != 0:
            print_error(f"Error building Docker image: {stderr}")
            return False
        print_success("Docker image built successfully")
        
        build_script = "../k8s/setup-minikube.sh"
        print("Running Minikube loading...")
        exit_code, stdout, stderr = run_command(build_script, check=True)
        if exit_code != 0:
            print_error(f"Error Pushing Docker image: {stderr}")
            return False

        print_success("Docker image loaded into Minikube successfully")
        return True

    except Exception as e:
        print_error(f"Error building and loading Docker image: {e}")
        return False

def check_minikube() -> bool:
    """Check if minikube is running.

    Returns:
        True if minikube is running, False otherwise.
    """
    print_step("Checking if minikube is running")
    try:
        exit_code, stdout, stderr = run_command(["minikube", "status"], check=False)
        if exit_code != 0:
            print_error("Minikube is not running")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False

        if "Running" not in stdout:
            print_error("Minikube is not running")
            print(f"stdout: {stdout}")
            return False

        print_success("Minikube is running")
        return True
    except Exception as e:
        print_error(f"Error checking minikube status: {e}")
        return False


def check_namespace() -> bool:
    """Check if the namespace exists.

    Returns:
        True if the namespace exists, False otherwise.
    """
    print_step(f"Checking if namespace {NAMESPACE} exists")
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        namespaces = v1.list_namespace()
        for ns in namespaces.items:
            if ns.metadata.name == NAMESPACE:
                print_success(f"Namespace {NAMESPACE} exists")
                return True

        print_error(f"Namespace {NAMESPACE} does not exist")
        return False
    except Exception as e:
        print_error(f"Error checking namespace: {e}")
        return False


def create_namespace() -> bool:
    """Create the namespace.

    Returns:
        True if the namespace was created, False otherwise.
    """
    print_step(f"Creating namespace {NAMESPACE}")
    try:
        exit_code, stdout, stderr = run_command(
            ["kubectl", "create", "namespace", NAMESPACE], check=False
        )
        if exit_code != 0 and "already exists" not in stderr:
            print_error(f"Error creating namespace: {stderr}")
            return False

        print_success(f"Namespace {NAMESPACE} created or already exists")
        return True
    except Exception as e:
        print_error(f"Error creating namespace: {e}")
        return False


def deploy_overseer() -> Optional[int]:
    """Deploy the Overseer service to Minikube.

    Returns:
        The port forwarding PID if the service was deployed, None otherwise.
    """
    print_step("Deploying Overseer service to Minikube")
    try:
        # Make the deployment script executable if it's not already
        run_command(["chmod", "+x", "./deploy_to_minikube.sh"], check=False)
        
        # Run the deployment script with a timeout
        try:
            exit_code, stdout, stderr = run_command(["./deploy_to_minikube.sh"], timeout=300)
            if exit_code != 0:
                print_error(f"Error deploying Overseer: {stderr}")
                return None
            
            # Extract the port forwarding PID from the output
            for line in stdout.splitlines():
                if "Port forwarding is running with PID:" in line:
                    pid = int(line.split(":")[-1].strip())
                    print_success(f"Overseer deployed with port forwarding PID: {pid}")
                    return pid
            
            print_error("Could not find port forwarding PID in output")
            return None
        except subprocess.TimeoutExpired:
            # If the script times out, check if the port forwarding PID file exists
            if os.path.exists(".port_forward_pid"):
                with open(".port_forward_pid", "r") as f:
                    try:
                        pid = int(f.read().strip())
                        print_success(f"Overseer deployed with port forwarding PID: {pid} (from file)")
                        return pid
                    except (ValueError, IOError) as e:
                        print_error(f"Error reading port forwarding PID from file: {e}")
            
            print_error("Deployment script timed out and could not find port forwarding PID")
            return None
    except Exception as e:
        print_error(f"Error deploying Overseer: {e}")
        return None


def cleanup_overseer(port_forward_pid: Optional[int] = None) -> None:
    """Clean up the Overseer deployment.

    Args:
        port_forward_pid: The port forwarding PID.
    """
    print_step("Cleaning up Overseer deployment")
    try:
        # Make the cleanup script executable if it's not already
        run_command(["chmod", "+x", "./cleanup_minikube.sh"], check=False)
        
        # Run the cleanup script
        exit_code, stdout, stderr = run_command(["./cleanup_minikube.sh"])
        if exit_code != 0:
            print_error(f"Error cleaning up Overseer: {stderr}")
        else:
            print_success("Overseer deployment cleaned up")
    except Exception as e:
        print_error(f"Error cleaning up Overseer: {e}")
        
        # If we have the port forwarding PID, try to kill it directly
        if port_forward_pid:
            try:
                os.kill(port_forward_pid, 15)  # SIGTERM
                print_success(f"Killed port forwarding process with PID {port_forward_pid}")
            except Exception as e:
                print_error(f"Error killing port forwarding process: {e}")


def wait_for_overseer_ready() -> bool:
    """Wait for the Overseer service to be ready.

    Returns:
        True if the service is ready, False otherwise.
    """
    print_step("Waiting for Overseer service to be ready")
    try:
        # Wait for the service to start
        print("Waiting for Overseer service to start...")
        time.sleep(5)
        
        # Check if the service is running
        for _ in range(10):
            try:
                response = httpx.get(f"{OVERSEER_URL}/")
                if response.status_code == 200:
                    print_success("Overseer service is ready")
                    return True
            except Exception:
                time.sleep(1)
        
        print_error("Overseer service failed to start")
        return False
    except Exception as e:
        print_error(f"Error waiting for Overseer service: {e}")
        return False


def test_health_check() -> bool:
    """Test the health check endpoint.

    Returns:
        True if the test passed, False otherwise.
    """
    print_step("Testing health check endpoint")
    try:
        response = httpx.get(f"{OVERSEER_URL}/")
        if response.status_code != 200:
            print_error(f"Health check failed with status code {response.status_code}")
            return False
        
        data = response.json()
        if data.get("status") != "ok":
            print_error(f"Health check failed with response: {data}")
            return False
        
        print_success("Health check passed")
        return True
    except Exception as e:
        print_error(f"Error testing health check: {e}")
        return False


def test_version() -> bool:
    """Test the version endpoint.

    Returns:
        True if the test passed, False otherwise.
    """
    print_step("Testing version endpoint")
    try:
        response = httpx.get(f"{OVERSEER_URL}/version")
        if response.status_code != 200:
            print_error(f"Version check failed with status code {response.status_code}")
            return False
        
        data = response.json()
        if "version" not in data:
            print_error(f"Version check failed with response: {data}")
            return False
        
        print_success(f"Version check passed: {data['version']}")
        return True
    except Exception as e:
        print_error(f"Error testing version: {e}")
        return False


def test_create_deployment() -> Optional[str]:
    """Test creating a deployment.

    Returns:
        The deployment ID if the test passed, None otherwise.
    """
    print_step("Testing create deployment endpoint")
    try:
        # Create a deployment
        payload = {
            "environment_type": "claude",
            "tools": ["web-search", "code-interpreter"],
            "data": {
                "context": "This is some context for the agent"
            },
            "requirement": "Analyze the provided data and generate insights",
            "ttl_seconds": 600
        }
        
        response = httpx.post(
            f"{OVERSEER_URL}/deployments",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 201:
            print_error(f"Create deployment failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        if "id" not in data:
            print_error(f"Create deployment failed with response: {data}")
            return None
        
        deployment_id = data["id"]
        print_success(f"Create deployment passed: {deployment_id}")
        return deployment_id
    except Exception as e:
        print_error(f"Error testing create deployment: {e}")
        return None


def test_get_deployment(deployment_id: str) -> bool:
    """Test getting a deployment.

    Args:
        deployment_id: The deployment ID.

    Returns:
        True if the test passed, False otherwise.
    """
    print_step(f"Testing get deployment endpoint for {deployment_id}")
    try:
        # Wait for the deployment to be created
        print("Waiting for deployment to be created...")
        time.sleep(10)
        
        # Get the deployment
        response = httpx.get(f"{OVERSEER_URL}/deployments/{deployment_id}")
        
        if response.status_code != 200:
            print_error(f"Get deployment failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        if data.get("id") != deployment_id:
            print_error(f"Get deployment failed with response: {data}")
            return False
        
        print_success(f"Get deployment passed: {data['status']}")
        return True
    except Exception as e:
        print_error(f"Error testing get deployment: {e}")
        return False


def test_get_deployment_status(deployment_id: str) -> bool:
    """Test getting a deployment status.

    Args:
        deployment_id: The deployment ID.

    Returns:
        True if the test passed, False otherwise.
    """
    print_step(f"Testing get deployment status endpoint for {deployment_id}")
    try:
        response = httpx.get(f"{OVERSEER_URL}/deployments/{deployment_id}/status")
        
        if response.status_code != 200:
            print_error(f"Get deployment status failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        if data.get("id") != deployment_id:
            print_error(f"Get deployment status failed with response: {data}")
            return False
        
        print_success(f"Get deployment status passed: {data['status']}")
        return True
    except Exception as e:
        print_error(f"Error testing get deployment status: {e}")
        return False


def wait_for_deployment_running(deployment_id: str, timeout: int = TEST_TIMEOUT) -> bool:
    """Wait for a deployment to be running.

    Args:
        deployment_id: The deployment ID.
        timeout: The timeout in seconds.

    Returns:
        True if the deployment is running, False otherwise.
    """
    print_step(f"Waiting for deployment {deployment_id} to be running")
    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = httpx.get(f"{OVERSEER_URL}/deployments/{deployment_id}/status")
            
            if response.status_code != 200:
                print(f"Get deployment status failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                time.sleep(5)
                continue
            
            data = response.json()
            status = data.get("status")
            
            if status == "running":
                print_success(f"Deployment {deployment_id} is running")
                return True
            elif status in ["failed", "terminated"]:
                print_error(f"Deployment {deployment_id} failed or was terminated")
                return False
            
            print(f"Deployment status: {status}")
            time.sleep(5)
        
        print_error(f"Timeout waiting for deployment {deployment_id} to be running")
        return False
    except Exception as e:
        print_error(f"Error waiting for deployment: {e}")
        return False


def test_get_deployment_connection(deployment_id: str) -> bool:
    """Test getting a deployment connection.

    Args:
        deployment_id: The deployment ID.

    Returns:
        True if the test passed, False otherwise.
    """
    print_step(f"Testing get deployment connection endpoint for {deployment_id}")
    try:
        response = httpx.get(f"{OVERSEER_URL}/deployments/{deployment_id}/connect")
        
        if response.status_code != 200:
            print_error(f"Get deployment connection failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        if data.get("id") != deployment_id or "connection_details" not in data:
            print_error(f"Get deployment connection failed with response: {data}")
            return False
        
        print_success(f"Get deployment connection passed: {data['connection_details']}")
        return True
    except Exception as e:
        print_error(f"Error testing get deployment connection: {e}")
        return False


def test_delete_deployment(deployment_id: str) -> bool:
    """Test deleting a deployment.

    Args:
        deployment_id: The deployment ID.

    Returns:
        True if the test passed, False otherwise.
    """
    print_step(f"Testing delete deployment endpoint for {deployment_id}")
    try:
        response = httpx.delete(f"{OVERSEER_URL}/deployments/{deployment_id}")
        
        if response.status_code != 204:
            print_error(f"Delete deployment failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print_success(f"Delete deployment passed")
        
        # Verify that the deployment was deleted
        print("Verifying deployment was deleted...")
        time.sleep(5)
        
        config.load_kube_config()
        apps_v1 = client.AppsV1Api()
        
        try:
            apps_v1.read_namespaced_deployment(name=deployment_id, namespace=NAMESPACE)
            print_error(f"Deployment {deployment_id} still exists")
            return False
        except client.exceptions.ApiException as e:
            if e.status == 404:
                print_success(f"Deployment {deployment_id} was deleted")
                return True
            else:
                print_error(f"Error verifying deployment deletion: {e}")
                return False
    except Exception as e:
        print_error(f"Error testing delete deployment: {e}")
        return False


def run_integration_tests() -> bool:
    """Run the integration tests.

    Returns:
        True if all tests passed, False otherwise.
    """
    print_step("Running integration tests")
    
    # Test health check
    if not test_health_check():
        return False
    
    # Test version
    if not test_version():
        return False
    
    # Test create deployment
    deployment_id = test_create_deployment()
    if not deployment_id:
        return False
    
    # Test get deployment
    if not test_get_deployment(deployment_id):
        return False
    
    # Test get deployment status
    if not test_get_deployment_status(deployment_id):
        return False
    
    # Wait for deployment to be running
    if not wait_for_deployment_running(deployment_id):
        # Clean up even if the test fails
        test_delete_deployment(deployment_id)
        return False
    
    # Test get deployment connection
    if not test_get_deployment_connection(deployment_id):
        # Clean up even if the test fails
        test_delete_deployment(deployment_id)
        return False
    
    # Test delete deployment
    if not test_delete_deployment(deployment_id):
        return False
    
    print_success("All integration tests passed")
    return True


def check_service_account_permissions() -> bool:
    """Check if the service account has the necessary permissions.

    Returns:
        True if the service account has the necessary permissions, False otherwise.
    """
    print_step("Checking service account permissions")
    try:
        # Check if the service account exists
        exit_code, stdout, stderr = run_command(
            ["kubectl", "get", "serviceaccount", "overseer-sa", "-n", NAMESPACE], check=False
        )
        if exit_code != 0:
            print_error(f"Service account overseer-sa does not exist in namespace {NAMESPACE}")
            return False

        # Check if the role exists
        exit_code, stdout, stderr = run_command(
            ["kubectl", "get", "role", "overseer-role", "-n", NAMESPACE], check=False
        )
        if exit_code != 0:
            print_error(f"Role overseer-role does not exist in namespace {NAMESPACE}")
            return False

        # Check if the role binding exists
        exit_code, stdout, stderr = run_command(
            ["kubectl", "get", "rolebinding", "overseer-rolebinding", "-n", NAMESPACE], check=False
        )
        if exit_code != 0:
            print_error(f"RoleBinding overseer-rolebinding does not exist in namespace {NAMESPACE}")
            return False

        print_success("Service account has the necessary permissions")
        return True
    except Exception as e:
        print_error(f"Error checking service account permissions: {e}")
        return False


def main() -> int:
    """Run the integration test.

    Returns:
        0 if the test passed, 1 otherwise.
    """
    # Check if minikube is running
    if not check_minikube():
        return 1
    
    # Check if the namespace exists
    if not check_namespace():
        # Create the namespace
        if not create_namespace():
            return 1
    
    # Build and load the Docker image for the claude environment into Minikube
    if not build_and_load_docker_image():
        return 1
    
    # Deploy the Overseer service to Minikube
    port_forward_pid = deploy_overseer()
    if not port_forward_pid:
        return 1
    
    # Check if the service account has the necessary permissions
    if not check_service_account_permissions():
        print_error("Service account does not have the necessary permissions. This may cause tests to fail.")
        # Continue anyway, as the permissions might be set up differently
    
    # Wait for the Overseer service to be ready
    if not wait_for_overseer_ready():
        cleanup_overseer(port_forward_pid)
        return 1
    
    try:
        # Run the integration tests
        if not run_integration_tests():
            return 1
        
        return 0
    finally:
        # Clean up the Overseer deployment
        cleanup_overseer(port_forward_pid)

if __name__ == "__main__":
    sys.exit(main()) 