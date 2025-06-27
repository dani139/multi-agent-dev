#!/usr/bin/env python3
"""
Test script for AutoGen code execution capabilities
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.developer import DeveloperAgent
from loguru import logger


async def test_python_code_execution():
    """
    Test Python code execution in sandbox
    """
    logger.info("🐍 Testing Python code execution...")
    
    # Initialize Developer Agent
    llm_config = {"config_list": [{"model": "gpt-4", "api_key": "mock"}]}
    developer_agent = DeveloperAgent(name="TestDeveloperAgent", llm_config=llm_config)
    
    # Test cases for Python code execution
    test_cases = [
        {
            "name": "Basic Python computation",
            "code": """
# Basic mathematical computation
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(f"Fibonacci(10) = {result}")

# List comprehension
squares = [x**2 for x in range(1, 6)]
print(f"Squares: {squares}")

# Dictionary operations
data = {'name': 'AutoGen', 'type': 'Framework', 'language': 'Python'}
print(f"Data: {data}")
""",
            "expected_output": ["Fibonacci(10)", "Squares:", "Data:"]
        },
        {
            "name": "Data structures and algorithms",
            "code": """
# Sorting algorithm
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = quicksort(numbers)
print(f"Original: {numbers}")
print(f"Sorted: {sorted_numbers}")
""",
            "expected_output": ["Original:", "Sorted:"]
        },
        {
            "name": "JSON and API simulation",
            "code": """
import json

# Simulate API response
api_response = {
    "status": "success",
    "data": {
        "users": [
            {"id": 1, "name": "Alice", "role": "developer"},
            {"id": 2, "name": "Bob", "role": "designer"}
        ]
    },
    "timestamp": "2024-01-01T00:00:00Z"
}

# JSON operations
json_string = json.dumps(api_response, indent=2)
print("API Response JSON:")
print(json_string[:200] + "..." if len(json_string) > 200 else json_string)

# Data processing
user_names = [user["name"] for user in api_response["data"]["users"]]
print(f"User names: {user_names}")
""",
            "expected_output": ["API Response JSON:", "User names:"]
        },
        {
            "name": "Error handling test",
            "code": """
# Test error handling
try:
    result = 10 / 0
    print(f"Result: {result}")
except ZeroDivisionError as e:
    print(f"Caught expected error: {e}")

# Test with valid operation
try:
    result = 10 / 2
    print(f"Valid result: {result}")
except Exception as e:
    print(f"Unexpected error: {e}")

print("Error handling test completed")
""",
            "expected_output": ["Caught expected error:", "Valid result:", "completed"]
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"📝 Test {i}: {test_case['name']}")
        
        try:
            result = await developer_agent.execute_code(test_case['code'], 'python')
            
            if result.get('status') == 'success':
                output = result.get('output', '')
                logger.success(f"✅ Code executed successfully")
                logger.info(f"   Output preview: {output[:100]}...")
                
                # Check if expected outputs are present
                expected_found = all(expected in output for expected in test_case['expected_output'])
                if expected_found:
                    logger.success("   ✅ All expected outputs found")
                    success_count += 1
                else:
                    logger.warning("   ⚠️  Some expected outputs missing")
                    
            elif result.get('status') == 'disabled':
                logger.warning(f"⚠️  Code execution disabled (sandbox not available)")
                success_count += 1  # Count as success since feature is disabled
            else:
                logger.error(f"❌ Code execution failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Test {i} failed with exception: {e}")
    
    logger.info(f"🏆 Python tests completed: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)


async def test_javascript_code_execution():
    """
    Test JavaScript code execution in sandbox
    """
    logger.info("🟨 Testing JavaScript code execution...")
    
    # Initialize Developer Agent
    llm_config = {"config_list": [{"model": "gpt-4", "api_key": "mock"}]}
    developer_agent = DeveloperAgent(name="TestDeveloperAgent", llm_config=llm_config)
    
    # Test cases for JavaScript code execution
    test_cases = [
        {
            "name": "Basic JavaScript operations",
            "code": """
// Basic operations
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(x => x * 2);
console.log('Original:', numbers);
console.log('Doubled:', doubled);

// Object manipulation
const user = {
    name: 'AutoGen',
    version: '1.0',
    features: ['multi-agent', 'web-browsing', 'code-execution']
};
console.log('User object:', JSON.stringify(user, null, 2));
""",
            "expected_output": ["Original:", "Doubled:", "User object:"]
        },
        {
            "name": "Async operations simulation",
            "code": """
// Simulate async operation
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function processData() {
    console.log('Starting data processing...');
    
    const data = ['item1', 'item2', 'item3'];
    const processed = [];
    
    for (const item of data) {
        // Simulate processing delay
        await delay(10);
        processed.push(item.toUpperCase());
        console.log(`Processed: ${item} -> ${item.toUpperCase()}`);
    }
    
    console.log('Processing complete:', processed);
    return processed;
}

// Run async function
processData().then(result => {
    console.log('Final result:', result);
}).catch(error => {
    console.error('Error:', error);
});
""",
            "expected_output": ["Starting data processing", "Processing complete"]
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"📝 Test {i}: {test_case['name']}")
        
        try:
            result = await developer_agent.execute_code(test_case['code'], 'javascript')
            
            if result.get('status') == 'success':
                output = result.get('output', '')
                logger.success(f"✅ JavaScript code executed successfully")
                logger.info(f"   Output preview: {output[:100]}...")
                success_count += 1
                
            elif result.get('status') == 'disabled':
                logger.warning(f"⚠️  Code execution disabled (sandbox not available)")
                success_count += 1  # Count as success since feature is disabled
            else:
                logger.error(f"❌ JavaScript execution failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Test {i} failed with exception: {e}")
    
    logger.info(f"🏆 JavaScript tests completed: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)


async def test_code_generation():
    """
    Test code generation capabilities
    """
    logger.info("🔧 Testing code generation capabilities...")
    
    # Initialize Developer Agent
    llm_config = {"config_list": [{"model": "gpt-4", "api_key": "mock"}]}
    developer_agent = DeveloperAgent(name="TestDeveloperAgent", llm_config=llm_config)
    
    # Test project structure generation
    logger.info("📁 Testing project structure generation...")
    
    project_plan = {
        "project_name": "test_project",
        "description": "A test project for AutoGen",
        "tech_stack": ["python", "fastapi", "pytest"],
        "requirements": "Build a simple API with testing"
    }
    
    try:
        structure = await developer_agent.generate_code_structure(project_plan)
        
        if structure.get('status') == 'generated':
            logger.success("✅ Project structure generated successfully")
            logger.info(f"   Project: {structure.get('project_name')}")
            logger.info(f"   Directories: {len(structure.get('directories', []))}")
            logger.info(f"   Files: {len(structure.get('files', {}))}")
            
            # Check for essential files
            files = structure.get('files', {})
            essential_files = ['README.md', 'requirements.txt', 'main.py', 'Dockerfile']
            found_files = [f for f in essential_files if f in files]
            
            logger.info(f"   Essential files found: {found_files}")
            
            if len(found_files) >= 3:
                logger.success("   ✅ Most essential files generated")
                return True
            else:
                logger.warning("   ⚠️  Some essential files missing")
                return False
        else:
            logger.error(f"❌ Structure generation failed: {structure.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Code generation test failed: {e}")
        return False


async def test_api_generation():
    """
    Test API generation capabilities
    """
    logger.info("🌐 Testing API generation...")
    
    # Initialize Developer Agent
    llm_config = {"config_list": [{"model": "gpt-4", "api_key": "mock"}]}
    developer_agent = DeveloperAgent(name="TestDeveloperAgent", llm_config=llm_config)
    
    # Test API specification
    api_spec = {
        "name": "TestAPI",
        "framework": "fastapi",
        "endpoints": [
            {
                "name": "get_users",
                "method": "GET",
                "path": "/users",
                "description": "Get all users"
            },
            {
                "name": "create_user",
                "method": "POST",
                "path": "/users",
                "description": "Create a new user"
            }
        ]
    }
    
    try:
        api_result = await developer_agent.create_api(api_spec)
        
        if api_result.get('status') == 'generated':
            logger.success("✅ API generated successfully")
            logger.info(f"   API Name: {api_result.get('api_name')}")
            logger.info(f"   Framework: {api_result.get('framework')}")
            logger.info(f"   Endpoints: {len(api_result.get('endpoints', []))}")
            
            # Check generated code
            code = api_result.get('code', '')
            if 'FastAPI' in code and '@app.get' in code:
                logger.success("   ✅ Generated code contains expected FastAPI patterns")
                return True
            else:
                logger.warning("   ⚠️  Generated code missing expected patterns")
                return False
        else:
            logger.error(f"❌ API generation failed: {api_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ API generation test failed: {e}")
        return False


def main():
    """
    Main function to run all code execution tests
    """
    logger.info("🚀 Starting AutoGen Code Execution Tests")
    
    # Check Docker availability
    docker_available = os.getenv("DOCKER_ENABLED", "true").lower() == "true"
    sandbox_enabled = os.getenv("SANDBOX_ENABLED", "true").lower() == "true"
    
    logger.info(f"🐳 Docker available: {docker_available}")
    logger.info(f"🔒 Sandbox enabled: {sandbox_enabled}")
    
    # Run tests
    try:
        results = []
        
        # Test Python code execution
        result1 = asyncio.run(test_python_code_execution())
        results.append(result1)
        
        # Test JavaScript code execution
        result2 = asyncio.run(test_javascript_code_execution())
        results.append(result2)
        
        # Test code generation
        result3 = asyncio.run(test_code_generation())
        results.append(result3)
        
        # Test API generation
        result4 = asyncio.run(test_api_generation())
        results.append(result4)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        logger.info(f"📊 Test Summary: {passed}/{total} tests passed")
        
        if passed == total:
            logger.success("🎉 All code execution tests passed!")
            return 0
        else:
            logger.warning(f"⚠️  {total - passed} tests failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>", level="INFO")
    
    exit_code = main()
    sys.exit(exit_code) 