"""
Deployment API endpoints.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from overseer.k8s.client import KubernetesClient
from overseer.models.deployment import (
    DeploymentConnectionResponse,
    DeploymentRequest,
    DeploymentResponse,
    DeploymentStatus,
    DeploymentStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/deployments", tags=["deployments"])

# In-memory storage for deployments (in a production environment, this would be a database)
deployments: Dict[str, DeploymentResponse] = {}


def get_k8s_client() -> KubernetesClient:
    """Get the Kubernetes client.

    Returns:
        A Kubernetes client instance.
    """
    return KubernetesClient()


@router.post(
    "",
    response_model=DeploymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new deployment",
    description="Create a new deployment with the specified environment type, tools, data, and requirement.",
)
async def create_deployment(
    request: DeploymentRequest, k8s_client: KubernetesClient = Depends(get_k8s_client)
) -> DeploymentResponse:
    """Create a new deployment.

    Args:
        request: The deployment request.
        k8s_client: The Kubernetes client.

    Returns:
        The deployment response.
    """
    try:
        # Create deployment in Kubernetes
        deployment_id, connection_details = k8s_client.create_deployment(
            environment_type=request.environment_type,
            tools=request.tools,
            data=request.data,
            requirement=request.requirement,
            ttl_seconds=request.ttl_seconds or 3600,
        )
        
        # Create deployment response
        deployment = DeploymentResponse(
            id=deployment_id,
            status=DeploymentStatus.CREATING,
            environment_type=request.environment_type,
            created_at=datetime.utcnow().isoformat(),
            connection_details=None,  # Will be updated when deployment is ready
            message="Deployment is being created",
        )
        
        # Store deployment in memory
        deployments[deployment_id] = deployment
        
        return deployment
        
    except Exception as e:
        logger.error(f"Error creating deployment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating deployment: {str(e)}",
        )


@router.get(
    "/{deployment_id}",
    response_model=DeploymentResponse,
    summary="Get deployment details",
    description="Get details for a specific deployment.",
)
async def get_deployment(
    deployment_id: str, k8s_client: KubernetesClient = Depends(get_k8s_client)
) -> DeploymentResponse:
    """Get deployment details.

    Args:
        deployment_id: The ID of the deployment.
        k8s_client: The Kubernetes client.

    Returns:
        The deployment response.
    """
    # Check if deployment exists in memory
    if deployment_id not in deployments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found",
        )
    
    # Get deployment from memory
    deployment = deployments[deployment_id]
    
    # Update status from Kubernetes
    k8s_status = k8s_client.get_deployment_status(deployment_id)
    deployment.status = k8s_status
    
    # Update message based on status
    if k8s_status == DeploymentStatus.RUNNING:
        deployment.message = "Deployment is running"
        # Update connection details if not already set
        if not deployment.connection_details:
            deployment.connection_details = {
                "service_url": f"http://{deployment_id}.{k8s_client.namespace}.svc.cluster.local",
                "ingress_host": f"{deployment_id}.example.com",  # This would be configured based on your ingress setup
                "novnc_port": "6080",
            }
    elif k8s_status == DeploymentStatus.CREATING:
        deployment.message = "Deployment is being created"
    elif k8s_status == DeploymentStatus.FAILED:
        deployment.message = "Deployment failed"
    elif k8s_status == DeploymentStatus.TERMINATED:
        deployment.message = "Deployment has been terminated"
    
    return deployment


@router.get(
    "/{deployment_id}/status",
    response_model=DeploymentStatusResponse,
    summary="Get deployment status",
    description="Get the status of a specific deployment.",
)
async def get_deployment_status(
    deployment_id: str, k8s_client: KubernetesClient = Depends(get_k8s_client)
) -> DeploymentStatusResponse:
    """Get deployment status.

    Args:
        deployment_id: The ID of the deployment.
        k8s_client: The Kubernetes client.

    Returns:
        The deployment status response.
    """
    # Check if deployment exists in memory
    if deployment_id not in deployments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found",
        )
    
    # Get deployment from memory
    deployment = deployments[deployment_id]
    
    # Update status from Kubernetes
    k8s_status = k8s_client.get_deployment_status(deployment_id)
    deployment.status = k8s_status
    
    # Update message based on status
    if k8s_status == DeploymentStatus.RUNNING:
        message = "Deployment is running"
    elif k8s_status == DeploymentStatus.CREATING:
        message = "Deployment is being created"
    elif k8s_status == DeploymentStatus.FAILED:
        message = "Deployment failed"
    elif k8s_status == DeploymentStatus.TERMINATED:
        message = "Deployment has been terminated"
    else:
        message = None
    
    return DeploymentStatusResponse(
        id=deployment_id,
        status=k8s_status,
        message=message,
    )


@router.get(
    "/{deployment_id}/connect",
    response_model=DeploymentConnectionResponse,
    summary="Get deployment connection details",
    description="Get connection details for a specific deployment.",
)
async def get_deployment_connection(
    deployment_id: str, k8s_client: KubernetesClient = Depends(get_k8s_client)
) -> DeploymentConnectionResponse:
    """Get deployment connection details.

    Args:
        deployment_id: The ID of the deployment.
        k8s_client: The Kubernetes client.

    Returns:
        The deployment connection response.
    """
    # Check if deployment exists in memory
    if deployment_id not in deployments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found",
        )
    
    # Get deployment from memory
    deployment = deployments[deployment_id]
    
    # Update status from Kubernetes
    k8s_status = k8s_client.get_deployment_status(deployment_id)
    deployment.status = k8s_status
    
    # Check if deployment is running
    if k8s_status != DeploymentStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deployment {deployment_id} is not running (status: {k8s_status})",
        )
    
    # Update connection details if not already set
    if not deployment.connection_details:
        deployment.connection_details = {
            "service_url": f"http://{deployment_id}.{k8s_client.namespace}.svc.cluster.local",
            "ingress_host": f"{deployment_id}.example.com",  # This would be configured based on your ingress setup
            "novnc_port": "6080",
        }
    
    return DeploymentConnectionResponse(
        id=deployment_id,
        connection_details=deployment.connection_details,
    )


@router.delete(
    "/{deployment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a deployment",
    description="Delete a specific deployment.",
)
async def delete_deployment(
    deployment_id: str, k8s_client: KubernetesClient = Depends(get_k8s_client)
) -> None:
    """Delete a deployment.

    Args:
        deployment_id: The ID of the deployment.
        k8s_client: The Kubernetes client.
    """
    # Check if deployment exists in memory
    if deployment_id not in deployments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found",
        )
    
    try:
        # Delete deployment in Kubernetes
        k8s_client.delete_deployment(deployment_id)
        
        # Update status in memory
        deployments[deployment_id].status = DeploymentStatus.TERMINATED
        deployments[deployment_id].message = "Deployment has been terminated"
        
    except Exception as e:
        logger.error(f"Error deleting deployment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting deployment: {str(e)}",
        ) 