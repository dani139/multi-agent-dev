# 🍳 Coder Platform - Setup Cookbook

> **✅ VERIFIED WORKING SETUP** - Step-by-step guide for the successful Docker backend + React frontend

## 🎯 Overview

This cookbook provides the exact steps to set up the working Coder multi-agent development platform. This setup has been tested and verified to work correctly.

## 📋 Prerequisites

```bash
# Required software
- Docker Desktop (or Docker Engine + Docker Compose)
- Node.js 18+
- Git
- curl (for testing)

# Verify installations
docker --version
node --version
npm --version
git --version
```

## 🚀 Step-by-Step Setup

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd coder
```

### 2. Build Backend Container
```bash
# Build the Docker image for backend
docker build -f Dockerfile.backend -t coder-backend .

# Verify build completed successfully
docker images | grep coder-backend
```

### 3. Start Backend Container
```bash
# Run backend in detached mode
docker run -d -p 8080:8080 --name coder-backend coder-backend

# Check if container is running
docker ps | grep coder-backend

# View logs (optional)
docker logs coder-backend
```

### 4. Test Backend API
```bash
# Test health endpoint
curl http://localhost:8080/health
# Expected: {"status": "healthy", "agents_count": 1}

# Test API documentation
curl http://localhost:8080/docs
# Should return FastAPI docs HTML
```

### 5. Setup Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 6. Verify Complete Setup
```bash
# Frontend should be running at: http://localhost:3000
# Backend API should be at: http://localhost:8080
# Frontend should successfully connect to backend
```

## 🧪 Testing the Platform

### Create a Test Project
```bash
curl -X POST http://localhost:8080/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "Testing AutoGen integration",
    "directory": "/home/user/projects/test"
  }'
```

### List Projects
```bash
curl http://localhost:8080/projects
```

### Test File Reading (AutoGen)
```bash
# First get a project ID from the list above, then:
curl "http://localhost:8080/files/list/YOUR_PROJECT_ID"

curl -X POST http://localhost:8080/files/read \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "YOUR_PROJECT_ID",
    "file_path": "README.md"
  }'
```

### Start AI Conversation
```bash
curl -X POST http://localhost:8080/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "YOUR_PROJECT_ID",
    "title": "Code Analysis",
    "initial_message": "Please analyze my project structure"
  }'
```

## 🔧 Development Workflow

### Daily Development Routine
```bash
# 1. Start backend (if not running)
docker start coder-backend

# 2. Start frontend (if not running)
cd frontend && npm start

# 3. Develop with hot reload
# - Frontend changes update automatically
# - Backend runs in isolated container
```

### Making Backend Changes
```bash
# 1. Stop current container
docker stop coder-backend
docker rm coder-backend

# 2. Rebuild image with changes
docker build -f Dockerfile.backend -t coder-backend .

# 3. Start new container
docker run -d -p 8080:8080 --name coder-backend coder-backend

# 4. Test changes
curl http://localhost:8080/health
```

### Making Frontend Changes
```bash
# Frontend automatically hot reloads
# Just edit files in frontend/src/
# Changes appear immediately in browser
```

## 🐛 Troubleshooting

### Backend Issues

**Container won't start:**
```bash
# Check logs
docker logs coder-backend

# Common fix: rebuild image
docker build -f Dockerfile.backend -t coder-backend . --no-cache
```

**Port already in use:**
```bash
# Find what's using port 8080
lsof -i :8080

# Kill process or use different port
docker run -d -p 8081:8080 --name coder-backend coder-backend
```

**API not responding:**
```bash
# Check container status
docker ps -a | grep coder-backend

# Restart container
docker restart coder-backend
```

### Frontend Issues

**Dependencies not installing:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**React won't start:**
```bash
# Check Node.js version (needs 18+)
node --version

# Clear npm cache
npm cache clean --force
npm install
```

### Connection Issues

**Frontend can't reach backend:**
```bash
# Verify backend is running
curl http://localhost:8080/health

# Check frontend API configuration
# Should be pointing to http://localhost:8080
```

## 📁 Key Files Reference

### Backend Files
- `backend.py` - Main FastAPI application with AutoGen integration
- `Dockerfile.backend` - Docker configuration for backend
- `requirements-docker.txt` - Python dependencies for Docker
- `agents/` - AutoGen agent implementations

### Frontend Files
- `frontend/src/App.js` - Main React application
- `frontend/src/App.css` - Tailwind CSS styling
- `frontend/package.json` - Node.js dependencies
- `frontend/tailwind.config.js` - Tailwind configuration

### Configuration Files
- `docker-compose.dev.yml` - Development Docker Compose setup
- `.gitignore` - Git ignore patterns (includes autogen/ library)

## 🎯 Next Steps

Once setup is complete:

1. **Create Projects**: Use the React frontend to create and manage projects
2. **Import Code**: Add existing codebases for AI analysis
3. **Start Conversations**: Chat with AutoGen about your code
4. **Extend Features**: Add new agents or frontend components
5. **Deploy**: Scale up with production Docker configurations

## 📚 Additional Resources

- **API Documentation**: Visit http://localhost:8080/docs when backend is running
- **React DevTools**: Install browser extension for frontend debugging
- **Docker Desktop**: Use GUI for container management
- **AutoGen Docs**: https://microsoft.github.io/autogen/ for framework details

---

**Last Updated**: 2025-06-27 | **Status**: ✅ Fully tested and working 