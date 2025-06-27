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

class FileEditRequest(BaseModel):
    project_id: str
    file_path: str
    content: str
    operation: Optional[str] = "replace"  # replace, append, prepend

class FileSearchReplaceRequest(BaseModel):
    project_id: str
    file_path: str
    search_text: str
    replace_text: str

class FileCreateRequest(BaseModel):
    project_id: str
    file_path: str
    content: str

class DirectoryBrowseRequest(BaseModel):
    path: str

# AutoGen File Tools
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

class FileEditorTool:
    """AutoGen tool for editing project files"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    def edit_file(self, file_path: str, content: str, operation: str = "replace") -> str:
        """Edit a file in the project directory"""
        try:
            full_path = self.project_path / file_path
            
            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if operation == "replace":
                # Replace entire file content
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"✅ File {file_path} has been completely replaced"
                
            elif operation == "append":
                # Append to file
                with open(full_path, 'a', encoding='utf-8') as f:
                    f.write("\n" + content)
                return f"✅ Content appended to {file_path}"
                
            elif operation == "prepend":
                # Prepend to file
                existing_content = ""
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content + "\n" + existing_content)
                return f"✅ Content prepended to {file_path}"
                
            else:
                return f"❌ Unknown operation: {operation}. Use 'replace', 'append', or 'prepend'"
                
        except Exception as e:
            return f"❌ Error editing file {file_path}: {str(e)}"
    
    def search_and_replace(self, file_path: str, search_text: str, replace_text: str) -> str:
        """Search and replace text in a file"""
        try:
            full_path = self.project_path / file_path
            if not full_path.exists():
                return f"❌ File not found: {file_path}"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if search_text not in content:
                return f"❌ Search text not found in {file_path}"
            
            new_content = content.replace(search_text, replace_text)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return f"✅ Replaced '{search_text}' with '{replace_text}' in {file_path}"
            
        except Exception as e:
            return f"❌ Error during search and replace in {file_path}: {str(e)}"
    
    def create_file(self, file_path: str, content: str) -> str:
        """Create a new file"""
        try:
            full_path = self.project_path / file_path
            
            if full_path.exists():
                return f"❌ File already exists: {file_path}"
            
            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ Created new file: {file_path}"
            
        except Exception as e:
            return f"❌ Error creating file {file_path}: {str(e)}"

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
        # Avoid recursion - don't copy if source contains destination
        source_path = Path(local_path).resolve()
        dest_path = project_dir.resolve()
        
        if dest_path.is_relative_to(source_path):
            # Create symlink instead of copy to avoid recursion
            if project_dir.exists():
                shutil.rmtree(project_dir)
            project_dir.symlink_to(source_path)
            logger.info(f"Created symlink from {project_dir} to {source_path}")
        else:
            # Safe to copy
            if project_dir.exists():
                shutil.rmtree(project_dir)
            shutil.copytree(local_path, project_dir, ignore=shutil.ignore_patterns('.*', '__pycache__'))
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
    """Send a message in a conversation with file tagging and editing support"""
    if conversation_id not in conversations_registry:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations_registry[conversation_id]
    project_id = conversation["project_id"]
    project_path = projects_registry[project_id]["path"]
    
    # Add user message
    user_message = {
        "id": str(uuid.uuid4()),
        "sender": "user",
        "content": message.message,
        "timestamp": datetime.now().isoformat()
    }
    conversation["messages"].append(user_message)
    
    # Process message for file operations
    try:
        file_tool = FileReaderTool(project_path)
        editor_tool = FileEditorTool(project_path)
        
        # Extract file tags (@filename pattern)
        import re
        file_tags = re.findall(r'@([^\s]+)', message.message)
        
        ai_response = ""
        
        # Handle file editing requests
        if any(keyword in message.message.lower() for keyword in ['edit', 'modify', 'change', 'update', 'fix']):
            if file_tags:
                ai_response = "I can help you edit files! Here's what I found:\n\n"
                for file_tag in file_tags:
                    file_content = file_tool.read_file(file_tag)
                    ai_response += f"📄 **{file_tag}**:\n```\n{file_content}\n```\n\n"
                
                ai_response += "To edit a file, you can:\n"
                ai_response += "• Ask me to modify specific parts\n"
                ai_response += "• Request search and replace operations\n"
                ai_response += "• Tell me what changes you want to make\n\n"
                ai_response += "Example: 'Replace the function name in @app.py from old_name to new_name'"
            else:
                ai_response = "I can help you edit files! Please tag a file with @ (like @filename.py) and tell me what changes you want to make."
        
        # Handle file reading requests
        elif any(keyword in message.message.lower() for keyword in ['show', 'read', 'display', 'view']):
            if file_tags:
                ai_response = "Here are the files you requested:\n\n"
                for file_tag in file_tags:
                    file_content = file_tool.read_file(file_tag)
                    ai_response += f"📄 **{file_tag}**:\n```\n{file_content}\n```\n\n"
            else:
                file_list = file_tool.list_files()
                ai_response = f"I can show you files! Here are the available files:\n\n{file_list}\n\nTag any file with @ to view it (like @README.md)"
        
        # Handle analysis requests
        elif any(keyword in message.message.lower() for keyword in ['analyze', 'examine', 'review', 'check']):
            if file_tags:
                ai_response = "📊 **File Analysis**:\n\n"
                for file_tag in file_tags:
                    file_content = file_tool.read_file(file_tag)
                    # Simple analysis
                    lines = file_content.count('\n')
                    size = len(file_content)
                    
                    ai_response += f"📄 **{file_tag}**:\n"
                    ai_response += f"• Lines: {lines}\n"
                    ai_response += f"• Size: {size} characters\n"
                    
                    if file_tag.endswith('.py'):
                        ai_response += "• Type: Python file\n"
                        if 'def ' in file_content:
                            functions = len(re.findall(r'def \w+', file_content))
                            ai_response += f"• Functions: {functions}\n"
                        if 'class ' in file_content:
                            classes = len(re.findall(r'class \w+', file_content))
                            ai_response += f"• Classes: {classes}\n"
                    elif file_tag.endswith('.js'):
                        ai_response += "• Type: JavaScript file\n"
                        if 'function ' in file_content:
                            functions = len(re.findall(r'function \w+', file_content))
                            ai_response += f"• Functions: {functions}\n"
                    
                    ai_response += "\n"
            else:
                ai_response = "I can analyze files! Tag files with @ (like @app.py) to get detailed analysis."
        
        # Handle direct edit commands
        elif 'replace' in message.message.lower() and file_tags:
            # Try to extract search and replace patterns
            replace_match = re.search(r'replace\s+["\'](.+?)["\']\s+with\s+["\'](.+?)["\']', message.message, re.IGNORECASE)
            if replace_match:
                search_text = replace_match.group(1)
                replace_text = replace_match.group(2)
                
                ai_response = "🔧 **File Edit Results**:\n\n"
                for file_tag in file_tags:
                    result = editor_tool.search_and_replace(file_tag, search_text, replace_text)
                    ai_response += f"📄 {file_tag}: {result}\n"
            else:
                ai_response = "To replace text, use the format: 'Replace \"old text\" with \"new text\" in @filename.py'"
        
        # Default response
        if not ai_response:
            ai_response = "I'm here to help with your project! You can:\n\n"
            ai_response += "• **View files**: 'Show @README.md'\n"
            ai_response += "• **Edit files**: 'Edit @app.py to add a new function'\n"
            ai_response += "• **Analyze code**: 'Analyze @src/main.py'\n"
            ai_response += "• **Replace text**: 'Replace \"old_function\" with \"new_function\" in @app.py'\n\n"
            
            if file_tags:
                ai_response += "I see you tagged these files:\n"
                for file_tag in file_tags:
                    ai_response += f"• @{file_tag}\n"
                ai_response += "\nWhat would you like me to do with them?"
            else:
                file_list = file_tool.list_files()
                ai_response += f"Available files in your project:\n{file_list}"
        
        # Add AI response
        ai_message = {
            "id": str(uuid.uuid4()),
            "sender": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat(),
            "file_tags": file_tags if file_tags else []
        }
        conversation["messages"].append(ai_message)
        
        return {
            "message_id": ai_message["id"],
            "response": ai_response,
            "file_tags": file_tags
        }
        
    except Exception as e:
        logger.error(f"Failed to generate AI response: {e}")
        
        # Fallback response
        fallback_response = "I'm ready to help with your project. Tag files with @ and tell me what you'd like to do!"
        
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

# New file editing endpoints
@app.post("/files/edit")
async def edit_file(request: FileEditRequest):
    """Edit a file using AutoGen file editor"""
    if request.project_id not in projects_registry:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_registry[request.project_id]
    project_path = project["path"]
    
    try:
        editor_tool = FileEditorTool(project_path)
        result = editor_tool.edit_file(request.file_path, request.content, request.operation)
        
        return {
            "project_id": request.project_id,
            "file_path": request.file_path,
            "operation": request.operation,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to edit file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/files/search-replace")
async def search_replace_file(request: FileSearchReplaceRequest):
    """Search and replace text in a file"""
    if request.project_id not in projects_registry:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_registry[request.project_id]
    project_path = project["path"]
    
    try:
        editor_tool = FileEditorTool(project_path)
        result = editor_tool.search_and_replace(request.file_path, request.search_text, request.replace_text)
        
        return {
            "project_id": request.project_id,
            "file_path": request.file_path,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to search and replace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/files/create")
async def create_file(request: FileCreateRequest):
    """Create a new file"""
    if request.project_id not in projects_registry:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_registry[request.project_id]
    project_path = project["path"]
    
    try:
        editor_tool = FileEditorTool(project_path)
        result = editor_tool.create_file(request.file_path, request.content)
        
        return {
            "project_id": request.project_id,
            "file_path": request.file_path,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to create file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/tree/{project_id}")
async def get_file_tree(project_id: str):
    """Get complete file tree structure for a project"""
    if project_id not in projects_registry:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_registry[project_id]
    project_path = Path(project["path"])
    
    def build_tree(path: Path, prefix: str = "") -> dict:
        """Recursively build file tree"""
        tree = {
            "name": path.name,
            "path": str(path.relative_to(project_path)) if path != project_path else "",
            "type": "directory" if path.is_dir() else "file",
            "children": []
        }
        
        if path.is_dir():
            try:
                for item in sorted(path.iterdir()):
                    if not item.name.startswith('.'):
                        tree["children"].append(build_tree(item, prefix + "  "))
            except PermissionError:
                pass
        else:
            tree["size"] = path.stat().st_size
        
        return tree
    
    try:
        tree = build_tree(project_path)
        return {
            "project_id": project_id,
            "tree": tree
        }
        
    except Exception as e:
        logger.error(f"Failed to build file tree: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browse-directory")
async def browse_local_directory(request: DirectoryBrowseRequest):
    """Browse local filesystem directories for project import"""
    try:
        # Handle both Docker and local paths
        path_str = request.path
        if not path_str:
            path_str = "/home"  # Default path
            
        path = Path(path_str).expanduser()
        
        # For Docker environment, limit to safe paths
        if not path.exists():
            # Try common default paths
            for default_path in ["/home", "/tmp", "/app"]:
                test_path = Path(default_path)
                if test_path.exists() and test_path.is_dir():
                    path = test_path
                    break
            else:
                raise HTTPException(status_code=404, detail=f"Directory not found: {path_str}")
        
        if not path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        items = []
        try:
            for item in sorted(path.iterdir()):
                # Skip hidden files and directories
                if item.name.startswith('.'):
                    continue
                
                try:
                    item_info = {
                        "name": item.name,
                        "path": str(item),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    }
                    items.append(item_info)
                except (PermissionError, OSError):
                    # Skip items we can't read
                    continue
        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Get parent directory info
        parent = None
        if path.parent != path:
            parent = {
                "name": "..",
                "path": str(path.parent),
                "type": "directory"
            }
        
        return {
            "current_path": str(path),
            "parent": parent,
            "items": items,
            "total": len(items)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to browse directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/autocomplete/{project_id}")
async def get_file_autocomplete(project_id: str, query: str = ""):
    """Get file names for autocomplete in chat"""
    if project_id not in projects_registry:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_registry[project_id]
    project_path = Path(project["path"])
    
    try:
        files = []
        for item in project_path.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                rel_path = str(item.relative_to(project_path))
                if query.lower() in rel_path.lower():
                    files.append({
                        "path": rel_path,
                        "name": item.name,
                        "type": item.suffix[1:] if item.suffix else "file"
                    })
        
        return {
            "project_id": project_id,
            "query": query,
            "files": files[:20]  # Limit to 20 results
        }
        
    except Exception as e:
        logger.error(f"Failed to get file autocomplete: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 