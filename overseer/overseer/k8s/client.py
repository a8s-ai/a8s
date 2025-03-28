"""
Kubernetes client for the Overseer API.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

from overseer.models.deployment import DeploymentStatus

logger = logging.getLogger(__name__)


class KubernetesClient:
    """Client for interacting with Kubernetes."""

    def __init__(self, namespace: str = "a8s"):
        """Initialize the Kubernetes client.

        Args:
            namespace: The namespace to use for deployments.
        """
        self.namespace = namespace
        self._load_config()
        self.core_api = client.CoreV1Api()
        self.apps_api = client.AppsV1Api()
        self.networking_api = client.NetworkingV1Api()

    def _load_config(self) -> None:
        """Load Kubernetes configuration.

        Tries to load in-cluster config first, falls back to kubeconfig.
        """
        try:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration")
        except config.ConfigException:
            config.load_kube_config()
            logger.info("Loaded kubeconfig Kubernetes configuration")

    def create_deployment(
        self,
        environment_type: str,
        tools: List[str],
        data: Dict[str, str],
        requirement: str,
        ttl_seconds: int = 3600,
    ) -> Tuple[str, Dict[str, str]]:
        """Create a new deployment.

        Args:
            environment_type: Type of environment to deploy.
            tools: List of tools to include in the environment.
            data: Data to pass to the environment.
            requirement: The requirement or task for the agent to execute.
            ttl_seconds: Time to live in seconds for the deployment.

        Returns:
            Tuple of deployment ID and connection details.
        """
        deployment_id = f"a8s-{environment_type}-{uuid.uuid4().hex[:8]}"
        
        # Create deployment
        deployment = self._create_deployment_object(
            deployment_id, environment_type, tools, data, requirement
        )
        
        try:
            self.apps_api.create_namespaced_deployment(
                namespace=self.namespace, body=deployment
            )
            logger.info(f"Created deployment {deployment_id}")
            
            # Create service
            service = self._create_service_object(deployment_id)
            self.core_api.create_namespaced_service(
                namespace=self.namespace, body=service
            )
            logger.info(f"Created service for deployment {deployment_id}")
            
            # Create ingress
            ingress = self._create_ingress_object(deployment_id)
            self.networking_api.create_namespaced_ingress(
                namespace=self.namespace, body=ingress
            )
            logger.info(f"Created ingress for deployment {deployment_id}")
            
            # Return connection details
            connection_details = {
                "service_url": f"http://{deployment_id}.{self.namespace}.svc.cluster.local",
                "ingress_host": f"{deployment_id}.example.com",  # This would be configured based on your ingress setup
                "novnc_port": "6080",
            }
            
            return deployment_id, connection_details
            
        except ApiException as e:
            logger.error(f"Error creating deployment: {e}")
            raise

    def get_deployment_status(self, deployment_id: str) -> DeploymentStatus:
        """Get the status of a deployment.

        Args:
            deployment_id: The ID of the deployment.

        Returns:
            The status of the deployment.
        """
        try:
            deployment = self.apps_api.read_namespaced_deployment(
                name=deployment_id, namespace=self.namespace
            )
            
            # Check if deployment is available
            if deployment.status.available_replicas is None or deployment.status.available_replicas < 1:
                return DeploymentStatus.CREATING
            
            return DeploymentStatus.RUNNING
            
        except ApiException as e:
            if e.status == 404:
                return DeploymentStatus.TERMINATED
            logger.error(f"Error getting deployment status: {e}")
            return DeploymentStatus.FAILED

    def delete_deployment(self, deployment_id: str) -> None:
        """Delete a deployment.

        Args:
            deployment_id: The ID of the deployment.
        """
        try:
            # Delete ingress
            self.networking_api.delete_namespaced_ingress(
                name=deployment_id, namespace=self.namespace
            )
            logger.info(f"Deleted ingress for deployment {deployment_id}")
            
            # Delete service
            self.core_api.delete_namespaced_service(
                name=deployment_id, namespace=self.namespace
            )
            logger.info(f"Deleted service for deployment {deployment_id}")
            
            # Delete deployment
            self.apps_api.delete_namespaced_deployment(
                name=deployment_id, namespace=self.namespace
            )
            logger.info(f"Deleted deployment {deployment_id}")
            
        except ApiException as e:
            if e.status != 404:  # Ignore 404 errors (not found)
                logger.error(f"Error deleting deployment: {e}")
                raise

    def _create_deployment_object(
        self,
        deployment_id: str,
        environment_type: str,
        tools: List[str],
        data: Dict[str, str],
        requirement: str,
    ) -> client.V1Deployment:
        """Create a Kubernetes Deployment object.

        Args:
            deployment_id: The ID of the deployment.
            environment_type: Type of environment to deploy.
            tools: List of tools to include in the environment.
            data: Data to pass to the environment.
            requirement: The requirement or task for the agent to execute.

        Returns:
            A Kubernetes Deployment object.
        """
        # Convert tools and data to environment variables
        env_vars = [
            client.V1EnvVar(name="REQUIREMENT", value=requirement),
        ]
        
        # Add tools as comma-separated list
        if tools:
            env_vars.append(client.V1EnvVar(name="TOOLS", value=",".join(tools)))
        
        # Add data as individual environment variables
        for key, value in data.items():
            env_vars.append(client.V1EnvVar(name=f"DATA_{key.upper()}", value=value))
        
        # Create container
        container = client.V1Container(
            name=deployment_id,
            image=f"a8s-{environment_type}:latest",
            env=env_vars,
            image_pull_policy="Never",
            ports=[
                client.V1ContainerPort(container_port=6080, name="novnc"),
            ],
            resources=client.V1ResourceRequirements(
                requests={"cpu": "500m", "memory": "1Gi"},
                limits={"cpu": "2", "memory": "4Gi"},
            ),
        )
        
        # Create template
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": deployment_id}),
            spec=client.V1PodSpec(containers=[container]),
        )
        
        # Create spec
        spec = client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels={"app": deployment_id}),
            template=template,
        )
        
        # Create deployment
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=deployment_id),
            spec=spec,
        )
        
        return deployment

    def _create_service_object(self, deployment_id: str) -> client.V1Service:
        """Create a Kubernetes Service object.

        Args:
            deployment_id: The ID of the deployment.

        Returns:
            A Kubernetes Service object.
        """
        # Create service
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=deployment_id),
            spec=client.V1ServiceSpec(
                selector={"app": deployment_id},
                ports=[
                    client.V1ServicePort(port=6080, target_port=6080, name="novnc"),
                ],
            ),
        )
        
        return service

    def _create_ingress_object(self, deployment_id: str) -> client.V1Ingress:
        """Create a Kubernetes Ingress object.

        Args:
            deployment_id: The ID of the deployment.

        Returns:
            A Kubernetes Ingress object.
        """
        # Create ingress
        ingress = client.V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(name=deployment_id),
            spec=client.V1IngressSpec(
                rules=[
                    client.V1IngressRule(
                        host=f"{deployment_id}.example.com",  # This would be configured based on your ingress setup
                        http=client.V1HTTPIngressRuleValue(
                            paths=[
                                client.V1HTTPIngressPath(
                                    path="/",
                                    path_type="Prefix",
                                    backend=client.V1IngressBackend(
                                        service=client.V1IngressServiceBackend(
                                            name=deployment_id,
                                            port=client.V1ServiceBackendPort(
                                                number=6080,
                                            ),
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )
        
        return ingress 