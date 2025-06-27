# Multi-Agent Software Development Platform

A comprehensive multi-agent system powered by AutoGen for automated software development, testing, documentation, deployment, and maintenance.

## 🚀 Overview

This project implements a collaborative multi-agent system that can:

- **Code Generation & Modification**: Generate, review, and modify code files across multiple programming languages
- **Automated Testing**: Create and execute comprehensive test suites
- **Documentation Analysis**: Read and interpret technical documentation to inform development decisions
- **Code Execution**: Execute code in secure sandboxed environments
- **Web Research**: Browse the internet to gather information about tools, libraries, and best practices
- **Deployment Automation**: Handle deployment pipelines and infrastructure management
- **Quality Assurance**: Perform code reviews, security audits, and performance analysis

## 🏗️ Architecture

The system consists of specialized agents:

1. **Project Manager Agent**: Coordinates tasks, manages workflows, and ensures project coherence
2. **Developer Agent**: Writes, modifies, and refactors code across multiple languages
3. **QA Agent**: Creates tests, performs code reviews, and ensures quality standards
4. **DevOps Agent**: Handles deployment, CI/CD, and infrastructure management
5. **Research Agent**: Gathers information from documentation and web sources
6. **Documentation Agent**: Creates and maintains project documentation

## 🛠️ Features

### Core Capabilities
- **Multi-language Support**: Python, JavaScript, TypeScript, Go, Rust, Java, and more
- **Intelligent Code Review**: Automated code analysis and suggestion system
- **Test Automation**: Unit, integration, and end-to-end test generation
- **Documentation Generation**: Automatic README, API docs, and code comments
- **Deployment Pipelines**: Docker, Kubernetes, CI/CD automation
- **Security Scanning**: Vulnerability detection and mitigation suggestions

### Advanced Features
- **Web Browsing**: Real-time information gathering using Playwright
- **Code Execution**: Secure sandbox environments for testing
- **Tool Integration**: Seamless integration with popular development tools
- **Learning System**: Continuously improves based on project outcomes

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)
- Git
- OpenAI API key or compatible LLM endpoint

## 🚀 Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd multi-agent-dev
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. Build and run with Docker:
```bash
docker-compose up --build
```

4. Access the web interface at `http://localhost:8080`

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `GITHUB_TOKEN`: GitHub token for repository operations
- `PLAYWRIGHT_BROWSERS_PATH`: Path for Playwright browser binaries
- `SANDBOX_ENABLED`: Enable/disable code execution sandbox

### Agent Configuration

Agents can be configured via `config/agents.yaml`:

```yaml
agents:
  project_manager:
    model: "gpt-4"
    temperature: 0.1
    max_tokens: 2000
  
  developer:
    model: "gpt-4"
    temperature: 0.2
    max_tokens: 4000
    
  # ... other agent configurations
```

## 📚 Usage Examples

### Creating a New Project

```python
from multi_agent_dev import ProjectManager

pm = ProjectManager()
project = pm.create_project({
    "name": "my-web-app",
    "type": "web",
    "tech_stack": ["python", "fastapi", "react"],
    "requirements": "Build a todo app with authentication"
})

await project.execute()
```

### Running Tests

```python
from multi_agent_dev import QAAgent

qa = QAAgent()
test_results = await qa.run_full_test_suite("./project")
print(f"Tests passed: {test_results.passed}/{test_results.total}")
```

### Deploying Application

```python
from multi_agent_dev import DevOpsAgent

devops = DevOpsAgent()
deployment = await devops.deploy({
    "platform": "kubernetes",
    "environment": "production",
    "auto_scale": True
})
```

## 🧪 Testing AutoGen Features

The project includes comprehensive testing for AutoGen capabilities:

### Internet Browsing with Playwright
```bash
python tests/test_web_browsing.py
```

### Code Execution
```bash
python tests/test_code_execution.py
```

### Multi-Agent Conversations
```bash
python tests/test_agent_collaboration.py
```

## 📁 Project Structure

```
multi-agent-dev/
├── agents/                 # Agent implementations
│   ├── __init__.py
│   ├── project_manager.py
│   ├── developer.py
│   ├── qa_agent.py
│   ├── devops.py
│   └── research.py
├── config/                 # Configuration files
│   ├── agents.yaml
│   └── settings.yaml
├── tests/                  # Test suite
│   ├── test_agents.py
│   ├── test_web_browsing.py
│   └── test_code_execution.py
├── docker/                 # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── examples/               # Usage examples
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── main.py                # Main application entry point
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Project Wiki](https://github.com/yourusername/multi-agent-dev/wiki)
- [Issue Tracker](https://github.com/yourusername/multi-agent-dev/issues)

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Join our Discord community
- Email: support@multi-agent-dev.com

---

**Made with ❤️ by the Multi-Agent Development Team** 