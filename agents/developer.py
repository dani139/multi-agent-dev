"""
Developer Agent
Writes, modifies, and refactors code across multiple languages
"""

import asyncio
import os
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
import autogen
from loguru import logger
import tempfile
import docker


class DeveloperAgent(autogen.AssistantAgent):
    """
    Developer Agent specialized in code generation, modification, and execution
    """
    
    def __init__(self, name: str, llm_config: Dict, **kwargs):
        system_message = """You are a Developer AI Agent specialized in software development.

Your responsibilities include:
1. Writing clean, efficient, and well-documented code
2. Code refactoring and optimization
3. Debugging and error resolution
4. Implementing new features and functionality
5. Code review and quality assurance
6. Multi-language development (Python, JavaScript, TypeScript, Go, etc.)
7. API development and integration
8. Database design and implementation

You should:
- Write production-ready, tested code
- Follow best practices and coding standards
- Provide clear documentation and comments
- Implement proper error handling
- Consider security and performance implications
- Use appropriate design patterns
- Ensure code is maintainable and scalable

Always prioritize code quality, security, and maintainability."""

        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            **kwargs
        )
        
        self.code_cache = {}
        self.docker_client = None
        self.sandbox_enabled = os.getenv("SANDBOX_ENABLED", "true").lower() == "true"
        logger.info(f"Initialized Developer Agent: {name}")
        
        if self.sandbox_enabled:
            try:
                self.docker_client = docker.from_env()
                logger.info("Docker client initialized for code execution sandbox")
            except Exception as e:
                logger.warning(f"Docker not available: {e}")
                self.sandbox_enabled = False
    
    async def generate_code_structure(self, project_plan: Dict) -> Dict:
        """
        Generate initial code structure based on project plan
        """
        logger.info("Generating initial code structure")
        
        try:
            project_name = project_plan.get('project_name', 'default_project')
            
            # Create basic project structure
            structure = {
                "project_name": project_name,
                "directories": [
                    "src/",
                    "tests/",
                    "docs/",
                    "config/",
                    "scripts/",
                    "data/"
                ],
                "files": {
                    "README.md": self._generate_readme(project_plan),
                    "requirements.txt": self._generate_requirements(project_plan),
                    "main.py": self._generate_main_file(project_plan),
                    "config/settings.py": self._generate_config_file(project_plan),
                    "tests/test_main.py": self._generate_test_file(project_plan),
                    ".gitignore": self._generate_gitignore(),
                    "Dockerfile": self._generate_dockerfile(project_plan)
                },
                "status": "generated"
            }
            
            self.code_cache[project_name] = structure
            return structure
            
        except Exception as e:
            logger.error(f"Code structure generation failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def execute_code(self, code: str, language: str = "python") -> Dict:
        """
        Execute code in a secure sandbox environment
        """
        logger.info(f"Executing {language} code in sandbox")
        
        if not self.sandbox_enabled:
            return {
                "error": "Code execution sandbox is disabled",
                "status": "disabled"
            }
        
        try:
            if language.lower() == "python":
                return await self._execute_python_code(code)
            elif language.lower() in ["javascript", "js"]:
                return await self._execute_javascript_code(code)
            else:
                return {
                    "error": f"Language {language} not supported",
                    "status": "unsupported"
                }
                
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _execute_python_code(self, code: str) -> Dict:
        """
        Execute Python code in Docker container
        """
        try:
            # Create temporary file with code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run code in Docker container
            result = self.docker_client.containers.run(
                "python:3.11-slim",
                f"python -c \"{code}\"",
                remove=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Clean up temporary file
            os.unlink(temp_file)
            
            return {
                "output": result.decode('utf-8') if isinstance(result, bytes) else result,
                "status": "success",
                "language": "python"
            }
            
        except docker.errors.ContainerError as e:
            return {
                "error": e.stderr.decode('utf-8') if e.stderr else str(e),
                "status": "error",
                "language": "python"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "language": "python"
            }
    
    async def _execute_javascript_code(self, code: str) -> Dict:
        """
        Execute JavaScript code in Docker container
        """
        try:
            # Run JavaScript code in Node.js Docker container
            result = self.docker_client.containers.run(
                "node:18-slim",
                f"node -e \"{code}\"",
                remove=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "output": result.decode('utf-8') if isinstance(result, bytes) else result,
                "status": "success",
                "language": "javascript"
            }
            
        except docker.errors.ContainerError as e:
            return {
                "error": e.stderr.decode('utf-8') if e.stderr else str(e),
                "status": "error",
                "language": "javascript"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "language": "javascript"
            }
    
    async def create_api(self, api_spec: Dict) -> Dict:
        """
        Create API implementation based on specification
        """
        logger.info(f"Creating API: {api_spec.get('name', 'Unknown')}")
        
        try:
            api_name = api_spec.get('name', 'api')
            endpoints = api_spec.get('endpoints', [])
            framework = api_spec.get('framework', 'fastapi')
            
            if framework.lower() == 'fastapi':
                api_code = self._generate_fastapi_code(api_name, endpoints)
            elif framework.lower() == 'flask':
                api_code = self._generate_flask_code(api_name, endpoints)
            else:
                return {"error": f"Framework {framework} not supported", "status": "failed"}
            
            return {
                "api_name": api_name,
                "code": api_code,
                "framework": framework,
                "endpoints": endpoints,
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"API creation failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def execute_task(self, task: Dict) -> Dict:
        """
        Execute a specific development task
        """
        task_type = task.get('type', 'unknown')
        
        try:
            if task_type == 'generate_structure':
                project_plan = task.get('project_plan', {})
                return await self.generate_code_structure(project_plan)
                
            elif task_type == 'execute_code':
                code = task.get('code', '')
                language = task.get('language', 'python')
                return await self.execute_code(code, language)
                
            elif task_type == 'create_api':
                api_spec = task.get('api_spec', {})
                return await self.create_api(api_spec)
                
            else:
                return {
                    "error": f"Unknown development task type: {task_type}",
                    "status": "failed"
                }
                
        except Exception as e:
            logger.error(f"Development task execution failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _generate_readme(self, project_plan: Dict) -> str:
        """Generate README.md content"""
        project_name = project_plan.get('project_name', 'Project')
        return f"""# {project_name}

## Description
Auto-generated project structure by Multi-Agent Development Platform.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

## Testing
```bash
pytest tests/
```

## License
MIT License
"""
    
    def _generate_requirements(self, project_plan: Dict) -> str:
        """Generate requirements.txt content"""
        return """# Core dependencies
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
loguru>=0.7.0

# Development dependencies
pytest>=7.4.0
black>=23.11.0
flake8>=6.1.0
"""
    
    def _generate_main_file(self, project_plan: Dict) -> str:
        """Generate main.py file"""
        return '''#!/usr/bin/env python3
"""
Main application entry point
"""

from fastapi import FastAPI
from loguru import logger

app = FastAPI(title="Auto-Generated API")

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting application...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _generate_config_file(self, project_plan: Dict) -> str:
        """Generate configuration file"""
        return '''"""
Application configuration
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Auto-Generated App"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
    
    def _generate_test_file(self, project_plan: Dict) -> str:
        """Generate test file"""
        return '''"""
Test suite for main application
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
'''
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore file"""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/

# Logs
*.log
logs/

# Environment variables
.env

# Database
*.db
*.sqlite3

# Temporary files
tmp/
temp/
'''
    
    def _generate_dockerfile(self, project_plan: Dict) -> str:
        """Generate Dockerfile"""
        return '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
'''
    
    def _generate_fastapi_code(self, api_name: str, endpoints: List[Dict]) -> str:
        """Generate FastAPI code"""
        code = f'''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="{api_name}")

'''
        
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET').upper()
            path = endpoint.get('path', '/')
            description = endpoint.get('description', '')
            
            if method == 'GET':
                code += f'''@app.get("{path}")
async def {endpoint.get('name', 'get_handler')}():
    """{description}"""
    return {{"message": "Success"}}

'''
            elif method == 'POST':
                code += f'''@app.post("{path}")
async def {endpoint.get('name', 'post_handler')}(data: dict):
    """{description}"""
    return {{"message": "Created", "data": data}}

'''
        
        return code
    
    def _generate_flask_code(self, api_name: str, endpoints: List[Dict]) -> str:
        """Generate Flask code"""
        code = f'''from flask import Flask, request, jsonify

app = Flask(__name__)

'''
        
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET').upper()
            path = endpoint.get('path', '/')
            
            code += f'''@app.route("{path}", methods=["{method}"])
def {endpoint.get('name', 'handler')}():
    if request.method == "{method}":
        return jsonify({{"message": "Success"}})

'''
        
        code += '''
if __name__ == "__main__":
    app.run(debug=True)
'''
        
        return code 