#!/usr/bin/env python3
"""
Multi-Agent Software Development Platform
Main application entry point
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from loguru import logger
from pydantic import BaseModel
import autogen
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our agent modules
from agents.project_manager import ProjectManagerAgent
from agents.developer import DeveloperAgent
from agents.qa_agent import QAAgent
from agents.devops import DevOpsAgent
from agents.research import ResearchAgent

# Configure logging
logger.add("logs/app.log", rotation="10 MB", retention="7 days", level="INFO")

class ProjectRequest(BaseModel):
    name: str
    description: str
    tech_stack: List[str]
    requirements: str

class AgentResponse(BaseModel):
    agent_name: str
    response: str
    task_status: str
    artifacts: Optional[Dict] = None

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Development Platform",
    description="Automated software development using AutoGen multi-agent system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent registry
agent_registry: Dict[str, autogen.ConversableAgent] = {}

def initialize_agents():
    """Initialize all agents with proper configuration"""
    logger.info("Initializing multi-agent system...")
    
    # Get API configuration
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("No OpenAI API key found. Using mock configuration.")
        llm_config = {"config_list": [{"model": "gpt-4", "api_key": "mock"}]}
    else:
        llm_config = {
            "config_list": [
                {
                    "model": "gpt-4",
                    "api_key": api_key,
                    "temperature": float(os.getenv("TEMPERATURE", "0.1")),
                    "max_tokens": int(os.getenv("MAX_TOKENS", "4000"))
                }
            ]
        }
    
    try:
        # Initialize Project Manager Agent
        agent_registry["project_manager"] = ProjectManagerAgent(
            name="ProjectManager",
            llm_config=llm_config
        )
        
        # Initialize Developer Agent
        agent_registry["developer"] = DeveloperAgent(
            name="Developer", 
            llm_config=llm_config
        )
        
        # Initialize QA Agent
        agent_registry["qa"] = QAAgent(
            name="QAEngineer",
            llm_config=llm_config
        )
        
        # Initialize DevOps Agent
        agent_registry["devops"] = DevOpsAgent(
            name="DevOpsEngineer",
            llm_config=llm_config
        )
        
        # Initialize Research Agent
        agent_registry["research"] = ResearchAgent(
            name="ResearchAgent",
            llm_config=llm_config
        )
        
        logger.info(f"Successfully initialized {len(agent_registry)} agents")
        
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Multi-Agent Development Platform...")
    initialize_agents()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Multi-Agent Development Platform...")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Multi-Agent Development Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { color: #2c3e50; }
            .agent { background: #f8f9fa; padding: 20px; margin: 10px 0; border-radius: 8px; }
            .status { color: #27ae60; }
        </style>
    </head>
    <body>
        <h1 class="header">🤖 Multi-Agent Development Platform</h1>
        <p>Welcome to the automated software development system powered by AutoGen.</p>
        
        <div class="agent">
            <h3>Available Agents:</h3>
            <ul>
                <li><strong>Project Manager</strong> - Coordinates tasks and manages workflows</li>
                <li><strong>Developer</strong> - Writes and modifies code</li>
                <li><strong>QA Engineer</strong> - Creates tests and performs quality assurance</li>
                <li><strong>DevOps Engineer</strong> - Handles deployment and infrastructure</li>
                <li><strong>Research Agent</strong> - Gathers information and documentation</li>
            </ul>
        </div>
        
        <div class="agent">
            <h3>Quick Start:</h3>
            <p>• API Documentation: <a href="/docs">/docs</a></p>
            <p>• Health Check: <a href="/health">/health</a></p>
            <p>• Agent Status: <a href="/agents/status">/agents/status</a></p>
        </div>
        
        <div class="agent">
            <h3>Features:</h3>
            <p>✅ Multi-agent collaboration<br>
               ✅ Web browsing with Playwright<br>
               ✅ Code execution sandbox<br>
               ✅ Automated testing<br>
               ✅ Deployment automation</p>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents_count": len(agent_registry),
        "version": "1.0.0"
    }

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    return {
        "agents": list(agent_registry.keys()),
        "total_agents": len(agent_registry),
        "status": "active"
    }

@app.post("/project/create")
async def create_project(project: ProjectRequest, background_tasks: BackgroundTasks):
    """Create a new project using multi-agent collaboration"""
    logger.info(f"Creating new project: {project.name}")
    
    if "project_manager" not in agent_registry:
        raise HTTPException(status_code=500, detail="Project Manager agent not initialized")
    
    try:
        # Start project creation in background
        background_tasks.add_task(execute_project_creation, project)
        
        return {
            "message": f"Project '{project.name}' creation started",
            "status": "initiated",
            "project_id": project.name.lower().replace(" ", "_")
        }
        
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_project_creation(project: ProjectRequest):
    """Execute project creation using agents"""
    logger.info(f"Executing project creation for: {project.name}")
    
    try:
        pm = agent_registry["project_manager"]
        developer = agent_registry["developer"]
        qa = agent_registry["qa"]
        
        # Create project plan
        project_plan = await pm.create_project_plan(project.dict())
        logger.info(f"Project plan created: {project_plan}")
        
        # Generate initial code structure
        code_structure = await developer.generate_code_structure(project_plan)
        logger.info(f"Code structure generated: {code_structure}")
        
        # Create test suite
        test_suite = await qa.create_test_suite(code_structure)
        logger.info(f"Test suite created: {test_suite}")
        
    except Exception as e:
        logger.error(f"Project creation failed: {e}")

@app.post("/agents/{agent_name}/execute")
async def execute_agent_task(agent_name: str, task: Dict):
    """Execute a specific task with an agent"""
    if agent_name not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    agent = agent_registry[agent_name]
    
    try:
        # Execute task based on agent type
        if hasattr(agent, 'execute_task'):
            result = await agent.execute_task(task)
        else:
            result = {"message": f"Task received by {agent_name}", "task": task}
        
        return AgentResponse(
            agent_name=agent_name,
            response=str(result),
            task_status="completed"
        )
        
    except Exception as e:
        logger.error(f"Task execution failed for {agent_name}: {e}")
        return AgentResponse(
            agent_name=agent_name,
            response=f"Error: {str(e)}",
            task_status="failed"
        )

def main():
    """Main function to run the application"""
    logger.info("Starting Multi-Agent Development Platform...")
    
    # Configuration
    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "8080"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main() 