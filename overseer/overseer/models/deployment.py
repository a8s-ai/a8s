"""
Deployment models for the Overseer API.
"""

from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class DeploymentStatus(str, Enum):
    """Status of a deployment."""

    PENDING = "pending"
    CREATING = "creating"
    RUNNING = "running"
    FAILED = "failed"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


class DeploymentRequest(BaseModel):
    """Request model for creating a new deployment."""

    environment_type: str = Field(
        ..., description="Type of environment to deploy (e.g., 'claude')"
    )
    tools: List[str] = Field(
        default_factory=list, description="List of tools to include in the environment"
    )
    data: Dict[str, str] = Field(
        default_factory=dict, description="Data to pass to the environment"
    )
    requirement: str = Field(
        ..., description="The requirement or task for the agent to execute"
    )
    ttl_seconds: Optional[int] = Field(
        default=3600, description="Time to live in seconds for the deployment"
    )


class DeploymentResponse(BaseModel):
    """Response model for a deployment."""

    id: str = Field(..., description="Unique identifier for the deployment")
    status: DeploymentStatus = Field(..., description="Current status of the deployment")
    environment_type: str = Field(..., description="Type of environment deployed")
    created_at: str = Field(..., description="Timestamp when the deployment was created")
    connection_details: Optional[Dict[str, str]] = Field(
        None, description="Connection details for the deployment"
    )
    message: Optional[str] = Field(None, description="Additional information or error message")


class DeploymentStatusResponse(BaseModel):
    """Response model for checking deployment status."""

    id: str = Field(..., description="Unique identifier for the deployment")
    status: DeploymentStatus = Field(..., description="Current status of the deployment")
    message: Optional[str] = Field(None, description="Additional information or error message")


class DeploymentConnectionResponse(BaseModel):
    """Response model for getting connection details."""

    id: str = Field(..., description="Unique identifier for the deployment")
    connection_details: Dict[str, str] = Field(
        ..., description="Connection details for the deployment"
    ) 