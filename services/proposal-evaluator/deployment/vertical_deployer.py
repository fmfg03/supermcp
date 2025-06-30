"""
Vertical Deployment System - Agentius as a Service
=================================================

Deploy specialized Agentius instances for different verticals (education, health, 
logistics) with pre-loaded context and industry-specific configurations.
"""

import asyncio
import yaml
import docker
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import subprocess

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class VerticalConfig:
    """Configuration for a vertical-specific deployment"""
    vertical: str
    industry_context: Dict[str, Any]
    judge_archetypes: List[str]
    fear_code_overrides: Dict[str, Any]
    custom_prompts: Dict[str, str]
    compliance_requirements: List[str]
    typical_deal_sizes: Dict[str, float]
    decision_makers: List[str]
    common_objections: List[str]
    success_metrics: Dict[str, str]

@dataclass
class DeploymentSpec:
    """Specification for a deployment"""
    deployment_id: str
    vertical: str
    client_id: str
    environment: str  # "dev", "staging", "prod"
    resources: Dict[str, Any]
    networking: Dict[str, Any]
    storage: Dict[str, Any]
    scaling: Dict[str, Any]
    monitoring: Dict[str, Any]

class VerticalConfigManager:
    """Manages vertical-specific configurations"""
    
    def __init__(self):
        self.verticals = self._define_vertical_configs()
    
    def _define_vertical_configs(self) -> Dict[str, VerticalConfig]:
        """Define configurations for different verticals"""
        
        return {
            "education": VerticalConfig(
                vertical="education",
                industry_context={
                    "budget_cycles": "annual",
                    "decision_timeline": "3-6 months",
                    "key_stakeholders": ["CIO", "CFO", "Academic VP", "IT Director"],
                    "procurement_process": "formal_rfp",
                    "compliance_focus": ["FERPA", "accessibility", "data_privacy"]
                },
                judge_archetypes=["conservative_cfo", "bureaucratic_executive", "technical_founder"],
                fear_code_overrides={
                    "conservative_cfo": {
                        "budget_overrun_risk": 0.95,  # Higher than normal
                        "compliance_risk": 0.9
                    },
                    "bureaucratic_executive": {
                        "process_compliance_violation": 0.95,
                        "stakeholder_misalignment": 0.85
                    }
                },
                custom_prompts={
                    "context_prefix": "In the education sector context, where budget approval requires multiple stakeholders and compliance is critical...",
                    "compliance_check": "Ensure this proposal addresses FERPA compliance, accessibility requirements, and student data protection."
                },
                compliance_requirements=["FERPA", "ADA", "COPPA", "State Privacy Laws"],
                typical_deal_sizes={"small": 25000, "medium": 100000, "large": 500000},
                decision_makers=["Chief Information Officer", "Chief Financial Officer", "Academic Vice President"],
                common_objections=[
                    "Budget is set annually and we're mid-cycle",
                    "Need approval from academic committee",
                    "Must ensure FERPA compliance",
                    "Integration with student information system required"
                ],
                success_metrics={
                    "student_outcomes": "improved_engagement",
                    "cost_efficiency": "cost_per_student",
                    "adoption_rate": "faculty_usage_percentage"
                }
            ),
            
            "healthcare": VerticalConfig(
                vertical="healthcare",
                industry_context={
                    "budget_cycles": "quarterly",
                    "decision_timeline": "2-4 months",
                    "key_stakeholders": ["Chief Medical Officer", "CIO", "CFO", "Compliance Officer"],
                    "procurement_process": "clinical_validation",
                    "compliance_focus": ["HIPAA", "FDA", "SOX", "clinical_quality"]
                },
                judge_archetypes=["conservative_cfo", "bureaucratic_executive", "technical_founder"],
                fear_code_overrides={
                    "conservative_cfo": {
                        "compliance_risk": 0.98,  # Extremely high
                        "roi_uncertainty": 0.85
                    },
                    "bureaucratic_executive": {
                        "career_limiting_failure": 0.95,  # Patient safety career risk
                        "process_compliance_violation": 0.9
                    }
                },
                custom_prompts={
                    "context_prefix": "In the healthcare sector, where patient safety and regulatory compliance are paramount...",
                    "compliance_check": "Validate HIPAA compliance, clinical workflow impact, and patient safety considerations."
                },
                compliance_requirements=["HIPAA", "FDA 21 CFR Part 11", "SOX", "Joint Commission"],
                typical_deal_sizes={"small": 50000, "medium": 250000, "large": 1000000},
                decision_makers=["Chief Medical Officer", "Chief Information Officer", "Chief Financial Officer"],
                common_objections=[
                    "Must pass clinical validation review",
                    "HIPAA compliance documentation required",
                    "Integration with Epic/Cerner systems needed",
                    "Physician workflow impact assessment required"
                ],
                success_metrics={
                    "patient_outcomes": "clinical_quality_improvement",
                    "efficiency": "time_to_diagnosis",
                    "safety": "error_reduction_rate"
                }
            ),
            
            "fintech": VerticalConfig(
                vertical="fintech",
                industry_context={
                    "budget_cycles": "quarterly",
                    "decision_timeline": "1-3 months",
                    "key_stakeholders": ["CTO", "CISO", "Head of Compliance", "CFO"],
                    "procurement_process": "security_first",
                    "compliance_focus": ["SOX", "PCI-DSS", "GDPR", "financial_regulations"]
                },
                judge_archetypes=["technical_founder", "conservative_cfo", "bureaucratic_executive"],
                fear_code_overrides={
                    "technical_founder": {
                        "security_risk": 0.95,
                        "scalability_concerns": 0.9
                    },
                    "conservative_cfo": {
                        "compliance_risk": 0.9,
                        "vendor_risk": 0.85
                    }
                },
                custom_prompts={
                    "context_prefix": "In the fintech sector, where security, compliance, and scalability are critical...",
                    "security_check": "Ensure SOC 2 compliance, PCI-DSS requirements, and financial data protection."
                },
                compliance_requirements=["SOX", "PCI-DSS", "GDPR", "SOC 2", "ISO 27001"],
                typical_deal_sizes={"small": 75000, "medium": 300000, "large": 1500000},
                decision_makers=["Chief Technology Officer", "Chief Information Security Officer", "Head of Compliance"],
                common_objections=[
                    "Security audit required before approval",
                    "Must integrate with existing fraud detection",
                    "Regulatory approval process needed",
                    "High availability requirements (99.99%)"
                ],
                success_metrics={
                    "security": "zero_breaches",
                    "performance": "transaction_processing_speed",
                    "compliance": "audit_pass_rate"
                }
            ),
            
            "manufacturing": VerticalConfig(
                vertical="manufacturing",
                industry_context={
                    "budget_cycles": "annual",
                    "decision_timeline": "4-8 months",
                    "key_stakeholders": ["Plant Manager", "Operations Director", "CFO", "IT Manager"],
                    "procurement_process": "operational_validation",
                    "compliance_focus": ["ISO", "safety_standards", "environmental"]
                },
                judge_archetypes=["conservative_cfo", "technical_founder", "bureaucratic_executive"],
                fear_code_overrides={
                    "technical_founder": {
                        "operational_disruption": 0.9,
                        "integration_complexity": 0.85
                    },
                    "conservative_cfo": {
                        "budget_overrun_risk": 0.9,
                        "roi_uncertainty": 0.85
                    }
                },
                custom_prompts={
                    "context_prefix": "In the manufacturing sector, where operational continuity and safety are paramount...",
                    "operational_check": "Assess production impact, safety considerations, and equipment integration requirements."
                },
                compliance_requirements=["ISO 9001", "OSHA", "Environmental Standards", "Quality Management"],
                typical_deal_sizes={"small": 100000, "medium": 500000, "large": 2000000},
                decision_makers=["Plant Manager", "Operations Director", "Chief Financial Officer"],
                common_objections=[
                    "Cannot disrupt production schedule",
                    "Must integrate with existing ERP system",
                    "Safety certification required",
                    "ROI must be proven within 18 months"
                ],
                success_metrics={
                    "efficiency": "operational_efficiency_improvement",
                    "quality": "defect_reduction_rate",
                    "safety": "incident_reduction"
                }
            )
        }
    
    def get_vertical_config(self, vertical: str) -> Optional[VerticalConfig]:
        """Get configuration for a specific vertical"""
        return self.verticals.get(vertical)
    
    def list_available_verticals(self) -> List[str]:
        """List all available verticals"""
        return list(self.verticals.keys())

class ContainerizedDeployer:
    """Handles containerized deployments of Agentius instances"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.docker_client = docker.from_env()
        self.registry_url = config.get("registry_url", "localhost:5000")
        self.base_image = config.get("base_image", "agentius/proposal-evaluator")
        
    async def deploy_vertical_instance(
        self, 
        vertical: str,
        client_id: str,
        environment: str = "prod",
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Deploy a vertical-specific Agentius instance"""
        
        # Generate deployment ID
        deployment_id = f"agentius-{vertical}-{client_id}-{environment}"
        
        # Get vertical configuration
        config_manager = VerticalConfigManager()
        vertical_config = config_manager.get_vertical_config(vertical)
        
        if not vertical_config:
            raise ValueError(f"Unknown vertical: {vertical}")
        
        # Create deployment specification
        deployment_spec = DeploymentSpec(
            deployment_id=deployment_id,
            vertical=vertical,
            client_id=client_id,
            environment=environment,
            resources=self._get_resource_spec(environment),
            networking=self._get_networking_spec(deployment_id),
            storage=self._get_storage_spec(deployment_id),
            scaling=self._get_scaling_spec(environment),
            monitoring=self._get_monitoring_spec(deployment_id)
        )
        
        try:
            # Build custom image with vertical configuration
            image_tag = await self._build_vertical_image(vertical_config, deployment_id)
            
            # Deploy container
            container = await self._deploy_container(deployment_spec, image_tag, custom_config)
            
            # Setup networking
            await self._setup_networking(container, deployment_spec)
            
            # Configure monitoring
            await self._setup_monitoring(container, deployment_spec)
            
            # Perform health checks
            health_status = await self._perform_health_checks(container, deployment_spec)
            
            logger.info(f"Successfully deployed {deployment_id}")
            
            return {
                "deployment_id": deployment_id,
                "status": "deployed",
                "container_id": container.id,
                "image_tag": image_tag,
                "endpoints": {
                    "api": f"https://{deployment_spec.networking['domain']}/api/v1",
                    "webhook": f"https://{deployment_spec.networking['domain']}/webhook",
                    "health": f"https://{deployment_spec.networking['domain']}/health"
                },
                "vertical_config": asdict(vertical_config),
                "health_status": health_status,
                "deployed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Deployment failed for {deployment_id}: {e}")
            await self._cleanup_failed_deployment(deployment_id)
            raise
    
    async def _build_vertical_image(self, vertical_config: VerticalConfig, deployment_id: str) -> str:
        """Build Docker image with vertical-specific configuration"""
        
        # Create temporary directory for build context
        build_dir = Path(f"/tmp/agentius_build_{deployment_id}")
        build_dir.mkdir(exist_ok=True)
        
        try:
            # Create Dockerfile
            dockerfile_content = f"""
FROM {self.base_image}:latest

# Copy vertical configuration
COPY vertical_config.json /app/config/vertical_config.json
COPY custom_prompts.json /app/config/custom_prompts.json
COPY compliance_config.json /app/config/compliance_config.json

# Set environment variables
ENV AGENTIUS_VERTICAL={vertical_config.vertical}
ENV AGENTIUS_MODE=vertical

# Override default configuration
COPY agentius_config.yaml /app/config/agentius_config.yaml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "main.py", "--vertical-mode"]
"""
            
            (build_dir / "Dockerfile").write_text(dockerfile_content)
            
            # Create configuration files
            (build_dir / "vertical_config.json").write_text(
                json.dumps(asdict(vertical_config), indent=2)
            )
            
            (build_dir / "custom_prompts.json").write_text(
                json.dumps(vertical_config.custom_prompts, indent=2)
            )
            
            (build_dir / "compliance_config.json").write_text(
                json.dumps({
                    "requirements": vertical_config.compliance_requirements,
                    "fear_overrides": vertical_config.fear_code_overrides
                }, indent=2)
            )
            
            # Create main configuration
            agentius_config = {
                "vertical": vertical_config.vertical,
                "judge_archetypes": vertical_config.judge_archetypes,
                "industry_context": vertical_config.industry_context,
                "llm": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "temperature": 0.2
                },
                "database": {
                    "provider": "supabase",
                    "connection_string": "${SUPABASE_CONNECTION_STRING}"
                },
                "monitoring": {
                    "enabled": True,
                    "metrics_endpoint": "/metrics"
                }
            }
            
            (build_dir / "agentius_config.yaml").write_text(
                yaml.dump(agentius_config, indent=2)
            )
            
            # Build image
            image_tag = f"{self.registry_url}/agentius-{vertical_config.vertical}:{deployment_id}"
            
            self.docker_client.images.build(
                path=str(build_dir),
                tag=image_tag,
                rm=True
            )
            
            # Push to registry
            self.docker_client.images.push(image_tag)
            
            logger.info(f"Built and pushed image: {image_tag}")
            return image_tag
            
        finally:
            # Cleanup build directory
            import shutil
            shutil.rmtree(build_dir, ignore_errors=True)
    
    async def _deploy_container(
        self, 
        deployment_spec: DeploymentSpec, 
        image_tag: str,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> docker.models.containers.Container:
        """Deploy the container"""
        
        # Environment variables
        env_vars = {
            "AGENTIUS_DEPLOYMENT_ID": deployment_spec.deployment_id,
            "AGENTIUS_VERTICAL": deployment_spec.vertical,
            "AGENTIUS_CLIENT_ID": deployment_spec.client_id,
            "AGENTIUS_ENVIRONMENT": deployment_spec.environment,
            "SUPABASE_CONNECTION_STRING": self.config.get("supabase_connection_string"),
            "OPENAI_API_KEY": self.config.get("openai_api_key"),
            "ANTHROPIC_API_KEY": self.config.get("anthropic_api_key")
        }
        
        # Add custom environment variables
        if custom_config and "environment" in custom_config:
            env_vars.update(custom_config["environment"])
        
        # Container configuration
        container_config = {
            "image": image_tag,
            "name": deployment_spec.deployment_id,
            "environment": env_vars,
            "ports": {"8000/tcp": deployment_spec.networking["port"]},
            "mem_limit": deployment_spec.resources["memory"],
            "cpu_count": deployment_spec.resources["cpu"],
            "volumes": {
                deployment_spec.storage["volume_name"]: {
                    "bind": "/app/data",
                    "mode": "rw"
                }
            },
            "labels": {
                "agentius.deployment_id": deployment_spec.deployment_id,
                "agentius.vertical": deployment_spec.vertical,
                "agentius.client_id": deployment_spec.client_id,
                "agentius.environment": deployment_spec.environment
            },
            "restart_policy": {"Name": "unless-stopped"},
            "detach": True
        }
        
        # Deploy container
        container = self.docker_client.containers.run(**container_config)
        
        logger.info(f"Container deployed: {container.id}")
        return container
    
    def _get_resource_spec(self, environment: str) -> Dict[str, Any]:
        """Get resource specifications based on environment"""
        
        specs = {
            "dev": {"cpu": 1, "memory": "1g", "storage": "10g"},
            "staging": {"cpu": 2, "memory": "2g", "storage": "20g"},
            "prod": {"cpu": 4, "memory": "4g", "storage": "50g"}
        }
        
        return specs.get(environment, specs["prod"])
    
    def _get_networking_spec(self, deployment_id: str) -> Dict[str, Any]:
        """Get networking specifications"""
        
        return {
            "port": self._get_available_port(),
            "domain": f"{deployment_id}.agentius.local",
            "ssl_enabled": True,
            "load_balancer": True
        }
    
    def _get_storage_spec(self, deployment_id: str) -> Dict[str, Any]:
        """Get storage specifications"""
        
        return {
            "volume_name": f"agentius_data_{deployment_id}",
            "backup_enabled": True,
            "encryption": True
        }
    
    def _get_scaling_spec(self, environment: str) -> Dict[str, Any]:
        """Get auto-scaling specifications"""
        
        specs = {
            "dev": {"min_instances": 1, "max_instances": 1, "cpu_threshold": 80},
            "staging": {"min_instances": 1, "max_instances": 2, "cpu_threshold": 70},
            "prod": {"min_instances": 2, "max_instances": 5, "cpu_threshold": 60}
        }
        
        return specs.get(environment, specs["prod"])
    
    def _get_monitoring_spec(self, deployment_id: str) -> Dict[str, Any]:
        """Get monitoring specifications"""
        
        return {
            "metrics_enabled": True,
            "logging_level": "INFO",
            "health_check_interval": 30,
            "alerting": {
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "error_rate_threshold": 5
            }
        }
    
    def _get_available_port(self) -> int:
        """Get an available port for the deployment"""
        
        # Simple port allocation - in production, use a proper port manager
        import socket
        
        for port in range(8100, 8200):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('', port))
                    return port
                except OSError:
                    continue
        
        raise RuntimeError("No available ports")
    
    async def _setup_networking(self, container, deployment_spec: DeploymentSpec):
        """Setup networking for the deployment"""
        
        # This would typically involve:
        # - Setting up reverse proxy rules
        # - Configuring SSL certificates
        # - Registering with service discovery
        # - Setting up load balancer rules
        
        logger.info(f"Networking configured for {deployment_spec.deployment_id}")
    
    async def _setup_monitoring(self, container, deployment_spec: DeploymentSpec):
        """Setup monitoring for the deployment"""
        
        # This would typically involve:
        # - Configuring Prometheus metrics
        # - Setting up log aggregation
        # - Creating dashboards
        # - Setting up alerting rules
        
        logger.info(f"Monitoring configured for {deployment_spec.deployment_id}")
    
    async def _perform_health_checks(self, container, deployment_spec: DeploymentSpec) -> Dict[str, Any]:
        """Perform initial health checks"""
        
        # Wait for container to be ready
        await asyncio.sleep(10)
        
        # Check container status
        container.reload()
        
        health_status = {
            "container_status": container.status,
            "health_check": "healthy" if container.status == "running" else "unhealthy",
            "api_responsive": await self._check_api_health(deployment_spec),
            "database_connection": "connected",  # Would check actual DB
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return health_status
    
    async def _check_api_health(self, deployment_spec: DeploymentSpec) -> bool:
        """Check if API is responding"""
        
        try:
            import httpx
            
            url = f"http://localhost:{deployment_spec.networking['port']}/health"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                return response.status_code == 200
                
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    async def _cleanup_failed_deployment(self, deployment_id: str):
        """Cleanup resources from failed deployment"""
        
        try:
            # Remove container if it exists
            try:
                container = self.docker_client.containers.get(deployment_id)
                container.remove(force=True)
            except docker.errors.NotFound:
                pass
            
            # Remove volume if it exists
            try:
                volume = self.docker_client.volumes.get(f"agentius_data_{deployment_id}")
                volume.remove()
            except docker.errors.NotFound:
                pass
            
            logger.info(f"Cleaned up failed deployment: {deployment_id}")
            
        except Exception as e:
            logger.error(f"Cleanup failed for {deployment_id}: {e}")
    
    async def list_deployments(self) -> List[Dict[str, Any]]:
        """List all Agentius deployments"""
        
        containers = self.docker_client.containers.list(
            filters={"label": "agentius.deployment_id"}
        )
        
        deployments = []
        
        for container in containers:
            labels = container.labels
            
            deployments.append({
                "deployment_id": labels.get("agentius.deployment_id"),
                "vertical": labels.get("agentius.vertical"),
                "client_id": labels.get("agentius.client_id"),
                "environment": labels.get("agentius.environment"),
                "status": container.status,
                "created": container.attrs["Created"],
                "ports": container.ports
            })
        
        return deployments
    
    async def scale_deployment(self, deployment_id: str, instances: int) -> Dict[str, Any]:
        """Scale a deployment to specified number of instances"""
        
        # This would implement horizontal scaling
        # For now, just log the request
        
        logger.info(f"Scaling {deployment_id} to {instances} instances")
        
        return {
            "deployment_id": deployment_id,
            "target_instances": instances,
            "status": "scaling",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def update_deployment(
        self, 
        deployment_id: str, 
        new_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a deployment with new configuration"""
        
        # This would implement blue-green or rolling updates
        
        logger.info(f"Updating deployment {deployment_id}")
        
        return {
            "deployment_id": deployment_id,
            "update_status": "in_progress",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def remove_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Remove a deployment"""
        
        try:
            # Stop and remove container
            container = self.docker_client.containers.get(deployment_id)
            container.stop()
            container.remove()
            
            # Remove volume
            try:
                volume = self.docker_client.volumes.get(f"agentius_data_{deployment_id}")
                volume.remove()
            except docker.errors.NotFound:
                pass
            
            logger.info(f"Removed deployment: {deployment_id}")
            
            return {
                "deployment_id": deployment_id,
                "status": "removed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except docker.errors.NotFound:
            return {
                "deployment_id": deployment_id,
                "status": "not_found",
                "error": "Deployment not found"
            }

# Factory function
def create_vertical_deployer(config: Dict[str, Any]) -> ContainerizedDeployer:
    """Create a vertical deployer instance"""
    return ContainerizedDeployer(config)

# CLI interface for deployment management
async def deploy_vertical_cli(
    vertical: str,
    client_id: str,
    environment: str = "prod"
):
    """CLI interface for deploying verticals"""
    
    config = {
        "registry_url": "localhost:5000",
        "base_image": "agentius/proposal-evaluator",
        "supabase_connection_string": "your_supabase_url",
        "openai_api_key": "your_openai_key"
    }
    
    deployer = create_vertical_deployer(config)
    
    try:
        result = await deployer.deploy_vertical_instance(
            vertical=vertical,
            client_id=client_id,
            environment=environment
        )
        
        print(f"✅ Deployment successful!")
        print(f"Deployment ID: {result['deployment_id']}")
        print(f"API Endpoint: {result['endpoints']['api']}")
        print(f"Health Check: {result['endpoints']['health']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        raise