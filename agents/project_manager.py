"""
Project Manager Agent
Coordinates tasks, manages workflows, and ensures project coherence
"""

import asyncio
from typing import Dict, List, Any, Optional
import autogen
from loguru import logger


class ProjectManagerAgent(autogen.AssistantAgent):
    """
    Project Manager Agent that coordinates multi-agent collaboration
    and manages project workflows
    """
    
    def __init__(self, name: str, llm_config: Dict, **kwargs):
        system_message = """You are a Project Manager AI Agent specialized in coordinating software development projects.

Your responsibilities include:
1. Creating comprehensive project plans and breaking down requirements
2. Coordinating tasks between different specialist agents (Developer, QA, DevOps, Research)
3. Managing project timelines and ensuring deliverables are met
4. Making high-level architectural decisions
5. Ensuring code quality and project standards
6. Managing communication between team members

You should:
- Break down complex requirements into manageable tasks
- Assign appropriate tasks to specialist agents
- Monitor progress and provide guidance
- Ensure all deliverables meet quality standards
- Make decisions about technology stack and architecture
- Coordinate deployment and release processes

Always be clear, organized, and focus on practical solutions."""

        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            **kwargs
        )
        
        self.project_data = {}
        logger.info(f"Initialized Project Manager Agent: {name}")
    
    async def create_project_plan(self, project_requirements: Dict) -> Dict:
        """
        Create a comprehensive project plan based on requirements
        """
        logger.info(f"Creating project plan for: {project_requirements.get('name', 'Unknown')}")
        
        try:
            # Analyze requirements and create structured plan
            plan_prompt = f"""
            Create a detailed project plan for the following project:
            
            Name: {project_requirements.get('name', '')}
            Description: {project_requirements.get('description', '')}
            Tech Stack: {project_requirements.get('tech_stack', [])}
            Requirements: {project_requirements.get('requirements', '')}
            
            Please provide a structured project plan including:
            1. Project scope and objectives
            2. Technical architecture recommendations
            3. Development phases and milestones
            4. Task breakdown for each agent (Developer, QA, DevOps, Research)
            5. Timeline estimates
            6. Risk assessment and mitigation strategies
            7. Quality assurance requirements
            8. Deployment strategy
            
            Format the response as a structured plan.
            """
            
            # Generate plan using the agent's LLM
            plan_response = await self._generate_response(plan_prompt)
            
            # Store project data
            self.project_data[project_requirements.get('name', 'default')] = {
                'requirements': project_requirements,
                'plan': plan_response,
                'status': 'planned',
                'created_at': asyncio.get_event_loop().time()
            }
            
            return {
                'project_name': project_requirements.get('name', ''),
                'plan': plan_response,
                'status': 'planned',
                'next_steps': self._identify_next_steps(plan_response)
            }
            
        except Exception as e:
            logger.error(f"Failed to create project plan: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def coordinate_agents(self, task: Dict, agents: List[autogen.Agent]) -> Dict:
        """
        Coordinate multiple agents to work on a complex task
        """
        logger.info(f"Coordinating agents for task: {task.get('name', 'Unknown')}")
        
        try:
            # Create a group chat for agent coordination
            group_chat = autogen.GroupChat(
                agents=[self] + agents,
                messages=[],
                max_round=10
            )
            
            # Initialize group chat manager
            manager = autogen.GroupChatManager(
                groupchat=group_chat,
                llm_config=self.llm_config
            )
            
            # Start coordination
            coordination_message = f"""
            Task Coordination Request:
            
            Task: {task.get('name', '')}
            Description: {task.get('description', '')}
            Requirements: {task.get('requirements', [])}
            
            Please collaborate to complete this task. Each agent should contribute 
            according to their specialization.
            """
            
            # Initiate group conversation
            await manager.a_initiate_chat(
                self,
                message=coordination_message
            )
            
            return {
                'status': 'coordinated',
                'participants': [agent.name for agent in agents],
                'task': task
            }
            
        except Exception as e:
            logger.error(f"Agent coordination failed: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def monitor_progress(self, project_name: str) -> Dict:
        """
        Monitor project progress and provide status updates
        """
        if project_name not in self.project_data:
            return {'error': 'Project not found', 'status': 'not_found'}
        
        project = self.project_data[project_name]
        
        # Calculate progress metrics
        progress_data = {
            'project_name': project_name,
            'status': project.get('status', 'unknown'),
            'created_at': project.get('created_at'),
            'current_phase': self._get_current_phase(project),
            'completion_percentage': self._calculate_completion(project),
            'next_milestones': self._get_next_milestones(project),
            'blockers': self._identify_blockers(project)
        }
        
        return progress_data
    
    async def execute_task(self, task: Dict) -> Dict:
        """
        Execute a specific project management task
        """
        task_type = task.get('type', 'unknown')
        
        if task_type == 'create_plan':
            return await self.create_project_plan(task.get('requirements', {}))
        elif task_type == 'monitor':
            return await self.monitor_progress(task.get('project_name', ''))
        elif task_type == 'coordinate':
            return await self.coordinate_agents(task, task.get('agents', []))
        else:
            return {
                'error': f'Unknown task type: {task_type}',
                'status': 'failed'
            }
    
    async def _generate_response(self, prompt: str) -> str:
        """
        Generate a response using the agent's LLM configuration
        """
        try:
            # This would normally use the LLM to generate a response
            # For now, return a structured mock response
            return f"""
            Project Plan Generated:
            
            ## Project Overview
            Based on the provided requirements, I've analyzed the project scope and created a comprehensive development plan.
            
            ## Technical Architecture
            - Recommended architecture patterns and technologies
            - Database design considerations
            - API structure and endpoints
            - Frontend/backend separation strategy
            
            ## Development Phases
            1. **Setup & Planning Phase** (Week 1)
               - Environment setup
               - Repository initialization
               - CI/CD pipeline configuration
            
            2. **Core Development Phase** (Weeks 2-4)
               - Backend API development
               - Database implementation
               - Core business logic
            
            3. **Frontend Development Phase** (Weeks 3-5)
               - UI/UX implementation
               - Integration with backend APIs
               - Testing and optimization
            
            4. **Testing & QA Phase** (Week 5-6)
               - Unit test implementation
               - Integration testing
               - Performance testing
               - Security audit
            
            5. **Deployment Phase** (Week 6)
               - Production environment setup
               - Deployment automation
               - Monitoring and logging
            
            ## Task Distribution
            - **Developer Agent**: Core implementation, API development
            - **QA Agent**: Test suite creation, quality assurance
            - **DevOps Agent**: Infrastructure, deployment, monitoring
            - **Research Agent**: Technology research, best practices
            
            ## Quality Assurance
            - Code review requirements
            - Testing coverage goals
            - Performance benchmarks
            - Security standards
            
            ## Risk Assessment
            - Technology risks and mitigation
            - Timeline risks and contingencies
            - Resource allocation concerns
            """
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return f"Error generating response: {str(e)}"
    
    def _identify_next_steps(self, plan: str) -> List[str]:
        """Identify immediate next steps from the project plan"""
        return [
            "Initialize project repository",
            "Set up development environment", 
            "Create initial project structure",
            "Configure CI/CD pipeline",
            "Begin core development tasks"
        ]
    
    def _get_current_phase(self, project: Dict) -> str:
        """Determine current project phase"""
        return project.get('current_phase', 'Planning')
    
    def _calculate_completion(self, project: Dict) -> float:
        """Calculate project completion percentage"""
        return project.get('completion', 0.0)
    
    def _get_next_milestones(self, project: Dict) -> List[str]:
        """Get upcoming project milestones"""
        return project.get('milestones', [])
    
    def _identify_blockers(self, project: Dict) -> List[str]:
        """Identify current project blockers"""
        return project.get('blockers', []) 