#!/usr/bin/env python3
"""
Enhanced Multi-Agent Development Platform Backend
with Project Management and AutoGen File Tools
"""

from typing import Dict, List, Optional
from pathlib import Path
import os
import json
import shutil
from datetime import datetime
import uuid

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Logging
from loguru import logger

# AutoGen imports
import autogen
from autogen import AssistantAgent

# Initialize FastAPI app
app = FastAPI(
    title="Coder Multi-Agent Platform",
    description="Enhanced multi-agent development platform with project management",
    version="2.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage
projects_registry = {}
conversations_registry = {}
agent_registry = {}

# Pydantic models
class ProjectCreate(BaseModel):
    name: str
    description: str
    local_path: Optional[str] = None

class ConversationCreate(BaseModel):
    project_id: str
    title: str
    initial_message: str

class ConversationMessage(BaseModel):
    message: str

class FileReadRequest(BaseModel):
    project_id: str
    file_path: str

# AutoGen File Reading Tool
class FileReaderTool:
    """AutoGen tool for reading project files"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    def read_file(self, file_path: str) -> str:
        """Read a file from the project directory"""
        try:
            full_path = self.project_path / file_path
            if not full_path.exists():
                return f"File not found: {file_path}"
            
            if full_path.is_dir():
                return f"Path is a directory: {file_path}"
                
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            return f"File: {file_path}\n{'='*50}\n{content}\n{'='*50}"
            
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    def list_files(self, directory: str = "") -> str:
        """List files in a directory"""
        try:
            full_path = self.project_path / directory if directory else self.project_path
            if not full_path.exists():
                return f"Directory not found: {directory}"
                
            files = []
            for item in sorted(full_path.iterdir()):
                if item.name.startswith('.'):
                    continue
                    
                if item.is_dir():
                    files.append(f"📁 {item.name}/")
                else:
                    size = item.stat().st_size
                    files.append(f"📄 {item.name} ({size} bytes)")
            
            return f"Directory: {directory or '.'}\n" + "\n".join(files)
            
        except Exception as e:
            return f"Error listing directory {directory}: {str(e)}"

def initialize_agents():
    """Initialize the AutoGen agents"""
    logger.info("Initializing enhanced multi-agent system...")
    
    # AutoGen configuration
    api_key = os.getenv("OPENAI_API_KEY", "mock_key_for_demo")
    
    llm_config = {
        "config_list": [
            {
                "model": "gpt-4",
                "api_key": api_key
            }
        ]
    }
    
    try:
        # Initialize base conversation agent
        agent_registry["conversation"] = AssistantAgent(
            name="ConversationManager",
            llm_config=llm_config,
            system_message="You are a helpful assistant that manages conversations about projects."
        )
        
        logger.info(f"Successfully initialized {len(agent_registry)} agents")
        
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        logger.warning("Continuing without AutoGen agents for testing purposes")

# Project Management Functions
async def create_project_directory(project_id: str, project_name: str, local_path: str = None):
    """Create or link a project directory"""
    
    projects_dir = Path("./projects")
    projects_dir.mkdir(exist_ok=True)
    
    project_dir = projects_dir / project_id
    
    if local_path and Path(local_path).exists():
        # Copy from local path
        if project_dir.exists():
            shutil.rmtree(project_dir)
        shutil.copytree(local_path, project_dir)
        logger.info(f"Copied project from {local_path} to {project_dir}")
    else:
        # Create empty project structure
        project_dir.mkdir(exist_ok=True)
        (project_dir / "README.md").write_text(f"# {project_name}\n\nProject created at {datetime.now()}")
        logger.info(f"Created new project directory: {project_dir}")
    
    return str(project_dir)

# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Starting Enhanced Multi-Agent Development Platform...")
    initialize_agents()
    
    # Create required directories (works both in Docker and locally)
    projects_dir = Path("./projects")
    conversations_dir = Path("./conversations")
    projects_dir.mkdir(exist_ok=True)
    conversations_dir.mkdir(exist_ok=True)
    
    logger.info("Application startup complete")

@app.get("/")
async def root():
    """Root endpoint with enhanced interface"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Coder - Multi-Agent Platform</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }
            .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .feature { display: inline-block; margin: 10px; padding: 15px; background: #e3f2fd; border-radius: 5px; }
            .button { background: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
            .button:hover { background: #1976D2; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Coder - Multi-Agent Development Platform</h1>
                <p>Enhanced with Project Management and AutoGen File Tools</p>
            </div>
            
            <div class="card">
                <h2>🚀 Quick Actions</h2>
                <a href="/docs" class="button">API Documentation</a>
                <a href="/health" class="button">Health Check</a>
                <a href="/projects" class="button">View Projects</a>
            </div>
            
            <div class="card">
                <h2>✨ New Features</h2>
                <div class="feature">📁 Project Management</div>
                <div class="feature">💬 AI Conversations</div>
                <div class="feature">📂 File Reading Tools</div>
                <div class="feature">🔍 Code Analysis</div>
                <div class="feature">🤝 Multi-Agent Collaboration</div>
            </div>
            
            <div class="card">
                <h2>🛠️ Available Endpoints</h2>
                <p><strong>POST /projects</strong> - Create new project</p>
                <p><strong>GET /projects</strong> - List all projects</p>
                <p><strong>POST /conversations</strong> - Start new conversation</p>
                <p><strong>POST /conversations/{id}/messages</strong> - Send message</p>
                <p><strong>POST /files/read</strong> - Read project files</p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Enhanced health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "agents_count": len(agent_registry),
        "projects_count": len(projects_registry),
        "conversations_count": len(conversations_registry),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/projects")
async def create_project(project: ProjectCreate):
    """Create a new project"""
    project_id = str(uuid.uuid4())
    
    try:
        # Create project directory
        project_path = await create_project_directory(
            project_id, 
            project.name, 
            project.local_path
        )
        
        # Store project info
        projects_registry[project_id] = {
            "id": project_id,
            "name": project.name,
            "description": project.description,
            "path": project_path,
            "created_at": datetime.now().isoformat(),
            "local_path": project.local_path
        }
        
        logger.info(f"Created project: {project.name} (ID: {project_id})")
        
        return {
            "project_id": project_id,
            "message": f"Project '{project.name}' created successfully",
            "path": project_path
        }
        
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects")
async def list_projects():
    """List all projects"""
    return {
        "projects": list(projects_registry.values()),
        "total": len(projects_registry)
    }

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    if project_id not in projects_registry:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_registry[project_id]
    
    # Get file structure
    project_path = Path(project["path"])
    files = []
    
    if project_path.exists():
        for item in project_path.rglob("*"):
            if not item.name.startswith('.') and item.is_file():
                rel_path = item.relative_to(project_path)
                files.append({
                    "path": str(rel_path),
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
    
    return {
        **project,
        "files": files,
        "file_count": len(files)
    }

@app.post("/conversations")
async def create_conversation(conversation: ConversationCreate):
    """Create a new conversation"""
    if conversation.project_id not in projects_registry:
        raise HTTPException(status_code=404, detail="Project not found")
    
    conversation_id = str(uuid.uuid4())
    
    conversations_registry[conversation_id] = {
        "id": conversation_id,
        "project_id": conversation.project_id,
        "title": conversation.title,
        "created_at": datetime.now().isoformat(),
        "messages": [{
            "id": str(uuid.uuid4()),
            "sender": "user",
            "content": conversation.initial_message,
            "timestamp": datetime.now().isoformat()
        }]
    }
    
    logger.info(f"Created conversation: {conversation.title} (ID: {conversation_id})")
    
    return {
        "conversation_id": conversation_id,
        "message": "Conversation created successfully"
    }

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation details"""
    if conversation_id not in conversations_registry:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversations_registry[conversation_id]

@app.post("/conversations/{conversation_id}/messages")
async def send_message(conversation_id: str, message: ConversationMessage):
    """Send a message in a conversation"""
    if conversation_id not in conversations_registry:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations_registry[conversation_id]
    project_id = conversation["project_id"]
    
    # Add user message
    user_message = {
        "id": str(uuid.uuid4()),
        "sender": "user",
        "content": message.message,
        "timestamp": datetime.now().isoformat()
    }
    conversation["messages"].append(user_message)
    
    # Generate AI response
    try:
        ai_response = f"I've received your message: '{message.message}'. As a project analyst, I can help you analyze files, understand code structure, and provide insights about your project. What specific aspect would you like me to examine?"
        
        # If message contains file-related keywords, offer file operations
        if any(keyword in message.message.lower() for keyword in ['file', 'code', 'read', 'analyze', 'show']):
            project_path = projects_registry[project_id]["path"]
            file_tool = FileReaderTool(project_path)
            file_list = file_tool.list_files()
            ai_response += f"\n\nAvailable files in your project:\n{file_list}"
        
        # Add AI response
        ai_message = {
            "id": str(uuid.uuid4()),
            "sender": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        conversation["messages"].append(ai_message)
        
        return {
            "message_id": ai_message["id"],
            "response": ai_response
        }
        
    except Exception as e:
        logger.error(f"Failed to generate AI response: {e}")
        
        # Fallback response
        fallback_response = "I'm ready to help with your project. Please let me know what you'd like to discuss or analyze."
        
        ai_message = {
            "id": str(uuid.uuid4()),
            "sender": "assistant",
            "content": fallback_response,
            "timestamp": datetime.now().isoformat()
        }
        conversation["messages"].append(ai_message)
        
        return {
            "message_id": ai_message["id"],
            "response": fallback_response
        }

@app.post("/files/read")
async def read_file(request: FileReadRequest):
    """Read a file from a project using AutoGen tools"""
    if request.project_id not in projects_registry:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_registry[request.project_id]
    project_path = project["path"]
    
    try:
        file_tool = FileReaderTool(project_path)
        content = file_tool.read_file(request.file_path)
        
        return {
            "project_id": request.project_id,
            "file_path": request.file_path,
            "content": content
        }
        
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/list/{project_id}")
async def list_project_files(project_id: str, directory: str = ""):
    """List files in a project directory"""
    if project_id not in projects_registry:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_registry[project_id]
    project_path = project["path"]
    
    try:
        file_tool = FileReaderTool(project_path)
        file_list = file_tool.list_files(directory)
        
        return {
            "project_id": project_id,
            "directory": directory,
            "files": file_list
        }
        
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 