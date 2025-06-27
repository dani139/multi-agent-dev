"""
DevOps Agent
Handles deployment, CI/CD, and infrastructure management
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
import autogen
from loguru import logger


class DevOpsAgent(autogen.AssistantAgent):
    """
    DevOps Agent specialized in deployment and infrastructure management
    """
    
    def __init__(self, name: str, llm_config: Dict, **kwargs):
        system_message = """You are a DevOps Engineer AI Agent specialized in deployment and infrastructure management.

Your responsibilities include:
1. Container orchestration with Docker and Kubernetes
2. CI/CD pipeline setup and management
3. Infrastructure as Code (IaC) with Terraform/CloudFormation
4. Monitoring and logging setup
5. Security configuration and compliance
6. Performance optimization and scaling
7. Backup and disaster recovery planning

You should:
- Automate deployment processes
- Ensure high availability and scalability
- Implement security best practices
- Monitor system health and performance
- Manage infrastructure efficiently
- Plan for disaster recovery
- Optimize costs and resources

Always prioritize automation, security, and reliability."""

        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            **kwargs
        )
        
        self.deployment_cache = {}
        logger.info(f"Initialized DevOps Agent: {name}")
    
    async def create_deployment_config(self, project_spec: Dict) -> Dict:
        """
        Create deployment configuration for the project
        """
        logger.info("Creating deployment configuration")
        
        try:
            project_name = project_spec.get('name', 'default_project')
            
            deployment_config = {
                "project_name": project_name,
                "docker": {
                    "dockerfile": self._generate_dockerfile(),
                    "docker_compose": self._generate_docker_compose(),
                    "dockerignore": self._generate_dockerignore()
                },
                "kubernetes": {
                    "deployment.yaml": self._generate_k8s_deployment(),
                    "service.yaml": self._generate_k8s_service(),
                    "ingress.yaml": self._generate_k8s_ingress()
                },
                "ci_cd": {
                    "github_actions": self._generate_github_actions(),
                    "gitlab_ci": self._generate_gitlab_ci()
                },
                "monitoring": {
                    "prometheus": self._generate_prometheus_config(),
                    "grafana": self._generate_grafana_config()
                },
                "status": "generated"
            }
            
            self.deployment_cache[project_name] = deployment_config
            return deployment_config
            
        except Exception as e:
            logger.error(f"Deployment config creation failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def execute_task(self, task: Dict) -> Dict:
        """
        Execute a specific DevOps task
        """
        task_type = task.get('type', 'unknown')
        
        try:
            if task_type == 'create_deployment':
                project_spec = task.get('project_spec', {})
                return await self.create_deployment_config(project_spec)
            else:
                return {
                    "error": f"Unknown DevOps task type: {task_type}",
                    "status": "failed"
                }
                
        except Exception as e:
            logger.error(f"DevOps task execution failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile"""
        return '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
'''
    
    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml"""
        return '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
    restart: unless-stopped
'''
    
    def _generate_dockerignore(self) -> str:
        """Generate .dockerignore"""
        return '''__pycache__
*.pyc
.git
.pytest_cache
tests/
docs/
'''
    
    def _generate_k8s_deployment(self) -> str:
        """Generate Kubernetes deployment"""
        return '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:latest
        ports:
        - containerPort: 8000
'''
    
    def _generate_k8s_service(self) -> str:
        """Generate Kubernetes service"""
        return '''apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
'''
    
    def _generate_k8s_ingress(self) -> str:
        """Generate Kubernetes ingress"""
        return '''apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
'''
    
    def _generate_github_actions(self) -> str:
        """Generate GitHub Actions workflow"""
        return '''name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest
    - name: Run tests
      run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Build and deploy
      run: |
        echo "Deploying to production"
'''
    
    def _generate_gitlab_ci(self) -> str:
        """Generate GitLab CI configuration"""
        return '''stages:
  - test
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest

deploy:
  stage: deploy
  script:
    - echo "Deploying to production"
  only:
    - main
'''
    
    def _generate_prometheus_config(self) -> str:
        """Generate Prometheus configuration"""
        return '''global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'app'
    static_configs:
      - targets: ['app:8000']
'''
    
    def _generate_grafana_config(self) -> str:
        """Generate Grafana configuration"""
        return '''apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
''' 