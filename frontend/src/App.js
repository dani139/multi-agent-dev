import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { marked } from 'marked';
import './App.css';

// API configuration
const API_BASE = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8080';

// Configure marked for safe HTML rendering
marked.setOptions({
  breaks: true,
  gfm: true,
});

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
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Features</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>📁 Project Management</li>
            <li>💬 AI Conversations</li>
            <li>📂 File Reading Tools</li>
            <li>✏️ File Editing with AI</li>
            <li>🔍 Code Analysis</li>
            <li>🏷️ File Tagging (@file.py)</li>
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
      alert('Failed to create project: ' + error.message);
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

// Directory Browser Component
function DirectoryBrowser({ onSelectDirectory, onCancel, initialPath = process.env.HOME || '/home' }) {
  const [currentPath, setCurrentPath] = useState(initialPath);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    browseDirectory(currentPath);
  }, [currentPath]);

  const browseDirectory = async (path) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/browse-directory`, { path });
      setItems(response.data.items);
      setCurrentPath(response.data.current_path);
    } catch (error) {
      console.error('Failed to browse directory:', error);
      alert('Failed to access directory: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleItemClick = (item) => {
    if (item.type === 'directory') {
      setCurrentPath(item.path);
    }
  };

  const goToParent = () => {
    const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
    setCurrentPath(parentPath);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-4xl h-3/4 flex flex-col">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Select Project Directory</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={goToParent}
              className="text-blue-600 hover:text-blue-800"
              disabled={currentPath === '/'}
            >
              ↑ Parent
            </button>
            <span className="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded">{currentPath}</span>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-4">
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="space-y-1">
              {items.filter(item => item.type === 'directory').map((item) => (
                <div
                  key={item.path}
                  onClick={() => handleItemClick(item)}
                  className="flex items-center space-x-2 p-2 hover:bg-gray-100 rounded cursor-pointer"
                >
                  <span className="text-blue-500">📁</span>
                  <span className="text-sm">{item.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 border-t flex justify-between">
          <button
            onClick={onCancel}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition duration-200"
          >
            Cancel
          </button>
          <button
            onClick={() => onSelectDirectory(currentPath)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200"
          >
            Select This Directory
          </button>
        </div>
      </div>
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
  const [showDirectoryBrowser, setShowDirectoryBrowser] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleDirectorySelect = (path) => {
    setFormData({...formData, local_path: path});
    setShowDirectoryBrowser(false);
  };

  return (
    <>
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
              Project Directory
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={formData.local_path}
                onChange={(e) => setFormData({...formData, local_path: e.target.value})}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Choose or type directory path..."
              />
              <button
                type="button"
                onClick={() => setShowDirectoryBrowser(true)}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition duration-200"
              >
                Browse
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Choose an existing directory to import, or leave empty to create a new project
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

      {showDirectoryBrowser && (
        <DirectoryBrowser
          onSelectDirectory={handleDirectorySelect}
          onCancel={() => setShowDirectoryBrowser(false)}
        />
      )}
    </>
  );
}

// File Tree Component
function FileTree({ projectId, onFileSelect, selectedFile }) {
  const [tree, setTree] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFileTree();
  }, [projectId]);

  const fetchFileTree = async () => {
    try {
      const response = await axios.get(`${API_BASE}/files/tree/${projectId}`);
      setTree(response.data.tree);
    } catch (error) {
      console.error('Failed to fetch file tree:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderTreeNode = (node, depth = 0) => {
    const isSelected = selectedFile === node.path;
    const paddingLeft = depth * 16;

    return (
      <div key={node.path || 'root'}>
        <div
          className={`flex items-center py-1 px-2 cursor-pointer hover:bg-gray-100 ${isSelected ? 'bg-blue-100' : ''}`}
          style={{ paddingLeft: `${paddingLeft + 8}px` }}
          onClick={() => node.type === 'file' && onFileSelect(node.path)}
        >
          <span className="mr-2">
            {node.type === 'directory' ? '📁' : '📄'}
          </span>
          <span className="text-sm">{node.name}</span>
          {node.size && (
            <span className="ml-auto text-xs text-gray-500">
              {Math.round(node.size / 1024)}KB
            </span>
          )}
        </div>
        {node.children && node.children.map(child => renderTreeNode(child, depth + 1))}
      </div>
    );
  };

  if (loading) {
    return <div className="p-4 text-center">Loading files...</div>;
  }

  return (
    <div className="h-full overflow-auto">
      {tree && renderTreeNode(tree)}
    </div>
  );
}

// Project Detail Component
function ProjectDetail() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [selectedFile, setSelectedFile] = useState('README.md');
  const [fileContent, setFileContent] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  useEffect(() => {
    if (selectedFile) {
      fetchFileContent(selectedFile);
    }
  }, [selectedFile, projectId]);

  const fetchProject = async () => {
    try {
      const response = await axios.get(`${API_BASE}/projects/${projectId}`);
      setProject(response.data);
    } catch (error) {
      console.error('Failed to fetch project:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFileContent = async (filePath) => {
    try {
      const response = await axios.post(`${API_BASE}/files/read`, {
        project_id: projectId,
        file_path: filePath
      });
      setFileContent(response.data.content);
    } catch (error) {
      console.error('Failed to fetch file content:', error);
      setFileContent('Failed to load file content');
    }
  };

  const createConversation = async () => {
    try {
      const response = await axios.post(`${API_BASE}/conversations`, {
        project_id: projectId,
        title: 'New Conversation',
        initial_message: 'Hello! I want to discuss this project.'
      });
      navigate(`/projects/${projectId}/conversations/${response.data.conversation_id}`);
    } catch (error) {
      console.error('Failed to create conversation:', error);
      alert('Failed to create conversation');
    }
  };

  const renderFileContent = () => {
    if (!fileContent) return null;

    // Extract actual file content (remove the file path header)
    const contentMatch = fileContent.match(/={50}\n(.*)\n={50}/s);
    const actualContent = contentMatch ? contentMatch[1] : fileContent;

    // Render markdown for .md files
    if (selectedFile.endsWith('.md')) {
      return (
        <div 
          className="prose max-w-none"
          dangerouslySetInnerHTML={{ __html: marked(actualContent) }}
        />
      );
    }

    // For other files, show as code
    return (
      <pre className="whitespace-pre-wrap text-sm font-mono bg-gray-50 p-4 rounded">
        {actualContent}
      </pre>
    );
  };

  if (loading) {
    return <div className="text-center py-8">Loading project...</div>;
  }

  if (!project) {
    return <div className="text-center py-8">Project not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
          <p className="text-gray-600">{project.description}</p>
        </div>
        <button
          onClick={createConversation}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200"
        >
          Start AI Conversation
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-screen max-h-[800px]">
        {/* File Browser */}
        <div className="lg:col-span-1 bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h3 className="font-semibold text-gray-900">Files</h3>
          </div>
          <FileTree 
            projectId={projectId} 
            onFileSelect={setSelectedFile}
            selectedFile={selectedFile}
          />
        </div>

        {/* File Content */}
        <div className="lg:col-span-3 bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h3 className="font-semibold text-gray-900">
              {selectedFile || 'Select a file'}
            </h3>
          </div>
          <div className="p-4 h-full overflow-auto">
            {renderFileContent()}
          </div>
        </div>
      </div>
    </div>
  );
}

// Conversation View Component
function ConversationView() {
  const { projectId, conversationId } = useParams();
  const [conversation, setConversation] = useState(null);
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [autocompleteFiles, setAutocompleteFiles] = useState([]);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversation();
  }, [conversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages]);

  const fetchConversation = async () => {
    try {
      const response = await axios.get(`${API_BASE}/conversations/${conversationId}`);
      setConversation(response.data);
    } catch (error) {
      console.error('Failed to fetch conversation:', error);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || sending) return;

    setSending(true);
    try {
      await axios.post(`${API_BASE}/conversations/${conversationId}/messages`, {
        message: message
      });
      
      setMessage('');
      setShowAutocomplete(false);
      await fetchConversation();
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleMessageChange = async (e) => {
    const value = e.target.value;
    setMessage(value);

    // Check for @ symbol for file autocomplete
    const lastAtIndex = value.lastIndexOf('@');
    if (lastAtIndex !== -1) {
      const query = value.substring(lastAtIndex + 1);
      if (query.length >= 0) {
        try {
          const response = await axios.get(`${API_BASE}/files/autocomplete/${projectId}?query=${query}`);
          setAutocompleteFiles(response.data.files);
          setShowAutocomplete(true);
        } catch (error) {
          console.error('Failed to fetch autocomplete:', error);
        }
      }
    } else {
      setShowAutocomplete(false);
    }
  };

  const selectAutocompleteFile = (file) => {
    const lastAtIndex = message.lastIndexOf('@');
    const newMessage = message.substring(0, lastAtIndex + 1) + file.path + ' ';
    setMessage(newMessage);
    setShowAutocomplete(false);
  };

  if (!conversation) {
    return <div className="text-center py-8">Loading conversation...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h1 className="text-xl font-semibold text-gray-900">{conversation.title}</h1>
          <p className="text-sm text-gray-600">
            Conversation in project • Use @filename to tag files
          </p>
        </div>

        {/* Messages */}
        <div className="h-96 overflow-auto p-4 space-y-4">
          {conversation.messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                msg.sender === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-900'
              }`}>
                <div className="whitespace-pre-wrap">{msg.content}</div>
                <div className="text-xs opacity-75 mt-1">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="p-4 border-t">
          <div className="relative">
            <div className="flex space-x-2">
              <input
                type="text"
                value={message}
                onChange={handleMessageChange}
                placeholder="Type a message... Use @filename to tag files"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              />
              <button
                onClick={sendMessage}
                disabled={sending || !message.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition duration-200"
              >
                {sending ? 'Sending...' : 'Send'}
              </button>
            </div>

            {/* Autocomplete */}
            {showAutocomplete && autocompleteFiles.length > 0 && (
              <div className="absolute bottom-full left-0 right-0 bg-white border border-gray-300 rounded-md shadow-lg max-h-40 overflow-auto z-10">
                {autocompleteFiles.map((file) => (
                  <div
                    key={file.path}
                    onClick={() => selectAutocompleteFile(file)}
                    className="flex items-center px-3 py-2 hover:bg-gray-100 cursor-pointer"
                  >
                    <span className="mr-2">📄</span>
                    <span className="text-sm">{file.path}</span>
                    <span className="ml-auto text-xs text-gray-500">{file.type}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="mt-2 text-xs text-gray-500">
            💡 Try: &quot;Show @README.md&quot;, &quot;Edit @app.py&quot;, &quot;Analyze @src/main.js&quot;, &quot;Replace &apos;old&apos; with &apos;new&apos; in @file.py&quot;
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 