# 🤖 Coder - Multi-Agent Development Platform

> **✅ VERIFIED WORKING** - Docker backend + React frontend with AutoGen integration

A comprehensive multi-agent software development platform built with Microsoft's AutoGen framework, featuring project management, AI-powered code analysis, and real-time conversations about your codebase.

## 🚀 Quick Start (Tested & Working)

### Prerequisites
- Docker installed and running
- Node.js 18+ for frontend development
- Git for version control

### 1. Start Backend (Docker)
```bash
# Build and run backend container
docker build -f Dockerfile.backend -t coder-backend .
docker run -d -p 8080:8080 --name coder-backend coder-backend

# Verify backend is running
curl http://localhost:8080/health
```

### 2. Start Frontend (Local Development)
```bash
# Install and run React frontend
cd frontend && npm install && npm start

# Frontend available at: http://localhost:3000
# Backend API at: http://localhost:8080
```

## ✨ Key Features

### 📁 **Project Management**
- Create and manage development projects
- Import existing codebases from local directories
- Organize projects with descriptions and metadata

### 🤖 **AutoGen Integration**
- **File Reading Tools**: Analyze project files with AI
- **Code Conversations**: Discuss your codebase with AI agents
- **Project Analysis**: Understand code structure and patterns
- **Multi-Agent Workflows**: Specialized agents for different development tasks

### 🎨 **Modern UI**
- React frontend with Tailwind CSS
- Responsive design for desktop and mobile
- Real-time updates and hot reload development
- Intuitive project and conversation management

### 🐳 **Docker Deployment**
- Backend runs in isolated Docker container
- Frontend runs locally for fast development
- Production-ready containerized architecture

## 🛠️ API Endpoints (All Tested)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/projects` | POST | Create new project |
| `/projects` | GET | List all projects |
| `/projects/{id}` | GET | Get project details |
| `/conversations` | POST | Start AI conversation |
| `/conversations/{id}/messages` | POST | Send message to AI |
| `/files/read` | POST | Read project file with AutoGen |
| `/files/list/{project_id}` | GET | List project files |

## 📊 Technical Stack

- **Backend**: Python 3.11 + FastAPI + AutoGen + Docker
- **Frontend**: React 18 + Tailwind CSS + Axios
- **AI Framework**: Microsoft AutoGen v0.9.0
- **Deployment**: Docker containers + Local development
- **Architecture**: REST API with AutoGen file tools

## 🔧 Development

### Backend Development
```bash
# Make backend changes
# Edit backend.py or agents/

# Rebuild and restart container
docker stop coder-backend && docker rm coder-backend
docker build -f Dockerfile.backend -t coder-backend .
docker run -d -p 8080:8080 --name coder-backend coder-backend
```

### Frontend Development
```bash
# Frontend automatically hot reloads
cd frontend && npm start
# Make changes to src/ files - they update automatically
```

## 📋 Testing Checklist

- [x] AutoGen library loads successfully
- [x] Backend starts on port 8080 (in Docker)
- [x] Health endpoint returns 200 OK
- [x] Frontend loads on port 3000 (local hot reload)
- [x] Can create new projects via API
- [x] Can view project list via API
- [x] File reading tools work (AutoGen FileReaderTool)
- [x] File listing functionality works
- [x] AI conversations with project analysis
- [x] Docker builds complete successfully
- [x] Frontend communicates with Docker backend

## 🎯 Usage Examples

### Create a Project
```bash
curl -X POST http://localhost:8080/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My App", "description": "React application"}'
```

### Analyze Project Files
```bash
curl -X POST http://localhost:8080/files/read \
  -H "Content-Type: application/json" \
  -d '{"project_id": "PROJECT_ID", "file_path": "src/App.js"}'
```

### Start AI Conversation
```bash
curl -X POST http://localhost:8080/conversations \
  -H "Content-Type: application/json" \
  -d '{"project_id": "PROJECT_ID", "title": "Code Review", "initial_message": "Please analyze my code structure"}'
```

## 📚 Documentation

- **Setup Guide**: See [COOKBOOK.md](COOKBOOK.md) for detailed setup instructions
- **Architecture**: Check [.cursor/rules/](/.cursor/rules/) for project structure
- **API Docs**: Visit http://localhost:8080/docs when backend is running

## 🤝 Contributing

This is a working multi-agent development platform. Feel free to:
1. Add new AutoGen agents for specialized tasks
2. Extend the React frontend with additional features
3. Implement new API endpoints for enhanced functionality
4. Improve the Docker deployment and scaling

## 📄 License

This project is for educational and development purposes, showcasing AutoGen's capabilities in a real-world application.

---

**Status**: ✅ Fully functional and tested | **Last Updated**: 2025-06-27 