import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// API configuration
const API_BASE = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8080';

// Main App Component
function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link to="/" className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-lg">C</span>
                  </div>
                  <span className="font-semibold text-xl text-gray-900">Coder</span>
                </Link>
              </div>
              <div className="flex items-center space-x-4">
                <Link to="/" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  Dashboard
                </Link>
                <Link to="/projects" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  Projects
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects" element={<ProjectList />} />
            <Route path="/projects/:projectId" element={<ProjectDetail />} />
            <Route path="/projects/:projectId/conversations/:conversationId" element={<ConversationView />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

// Dashboard Component
function Dashboard() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await axios.get(`${API_BASE}/health`);
        setHealth(response.data);
      } catch (error) {
        console.error('Failed to fetch health:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchHealth();
  }, []);

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8">
        <h1 className="text-3xl font-bold mb-2">Welcome to Coder</h1>
        <p className="text-blue-100 text-lg">Multi-Agent Development Platform with AutoGen</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Status</h3>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">
              {health ? 'System Healthy' : 'System Offline'}
            </span>
          </div>
          {health && (
            <div className="mt-4 text-sm text-gray-500">
              <p>Agents: {health.agents_count}</p>
              <p>Projects: {health.projects_count}</p>
              <p>Conversations: {health.conversations_count}</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Features</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>📁 Project Management</li>
            <li>💬 AI Conversations</li>
            <li>📂 File Reading Tools</li>
            <li>🔍 Code Analysis</li>
            <li>🤝 Multi-Agent Collaboration</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Quick Actions</h3>
          <div className="space-y-2">
            <Link 
              to="/projects" 
              className="block w-full bg-blue-600 text-white text-center py-2 px-4 rounded-md hover:bg-blue-700 transition duration-200"
            >
              View Projects
            </Link>
            <a 
              href={`${API_BASE}/docs`} 
              target="_blank" 
              rel="noopener noreferrer"
              className="block w-full bg-gray-600 text-white text-center py-2 px-4 rounded-md hover:bg-gray-700 transition duration-200"
            >
              API Docs
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

// Project List Component
function ProjectList() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API_BASE}/projects`);
      setProjects(response.data.projects);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (projectData) => {
    try {
      const response = await axios.post(`${API_BASE}/projects`, projectData);
      await fetchProjects();
      setShowCreateForm(false);
      navigate(`/projects/${response.data.project_id}`);
    } catch (error) {
      console.error('Failed to create project:', error);
      alert('Failed to create project');
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading projects...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200"
        >
          Create Project
        </button>
      </div>

      {showCreateForm && (
        <CreateProjectForm 
          onSubmit={handleCreateProject}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div key={project.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition duration-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{project.name}</h3>
            <p className="text-gray-600 text-sm mb-4">{project.description}</p>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-500">
                Created {new Date(project.created_at).toLocaleDateString()}
              </span>
              <Link
                to={`/projects/${project.id}`}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                View →
              </Link>
            </div>
          </div>
        ))}
      </div>

      {projects.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📁</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
          <p className="text-gray-600 mb-4">Create your first project to get started with AI-powered development.</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition duration-200"
          >
            Create Your First Project
          </button>
        </div>
      )}
    </div>
  );
}

// Create Project Form Component
function CreateProjectForm({ onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    local_path: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Create New Project</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Project Name
          </label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="My Awesome Project"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            required
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows="3"
            placeholder="Describe your project..."
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Local Directory Path (Optional)
          </label>
          <input
            type="text"
            value={formData.local_path}
            onChange={(e) => setFormData({...formData, local_path: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="/path/to/existing/project"
          />
          <p className="text-xs text-gray-500 mt-1">
            Leave empty to create a new project, or specify a path to import an existing project
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200"
          >
            Create Project
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition duration-200"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

// Project Detail Component
function ProjectDetail() {
  // Implementation for project detail view with file browser and conversation management
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Project Detail</h1>
      <p className="text-gray-600">Project detail view with file browser and conversations coming soon...</p>
    </div>
  );
}

// Conversation View Component  
function ConversationView() {
  // Implementation for conversation interface with AI agents
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Conversation</h1>
      <p className="text-gray-600">AI conversation interface coming soon...</p>
    </div>
  );
}

export default App; 