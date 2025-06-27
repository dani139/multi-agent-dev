#!/usr/bin/env python3
"""
Test script for AutoGen web browsing capabilities using Playwright
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.research import ResearchAgent
from loguru import logger


async def test_web_browsing():
    """
    Test web browsing functionality with the Research Agent
    """
    logger.info("🌐 Testing AutoGen Web Browsing with Playwright")
    
    # Initialize Research Agent
    llm_config = {"config_list": [{"model": "gpt-4", "api_key": "mock"}]}
    research_agent = ResearchAgent(name="TestResearchAgent", llm_config=llm_config)
    
    try:
        # Test 1: Web Search
        logger.info("🔍 Test 1: Performing web search...")
        search_results = await research_agent.web_search("Python AutoGen library", max_results=3)
        
        if search_results:
            logger.success(f"✅ Web search successful! Found {len(search_results)} results")
            for i, result in enumerate(search_results, 1):
                logger.info(f"  {i}. {result.get('title', 'No title')}")
                logger.info(f"     URL: {result.get('url', 'No URL')}")
        else:
            logger.warning("⚠️  Web search returned no results")
        
        # Test 2: Documentation Scraping
        logger.info("📄 Test 2: Scraping documentation...")
        doc_url = "https://microsoft.github.io/autogen/"
        doc_data = await research_agent.scrape_documentation(doc_url)
        
        if doc_data and not doc_data.get('error'):
            logger.success(f"✅ Documentation scraping successful!")
            logger.info(f"  Title: {doc_data.get('title', 'No title')}")
            logger.info(f"  Content length: {len(doc_data.get('content', ''))}")
            logger.info(f"  Headings found: {len(doc_data.get('headings', []))}")
            logger.info(f"  Code blocks found: {len(doc_data.get('code_blocks', []))}")
        else:
            logger.warning(f"⚠️  Documentation scraping failed: {doc_data.get('error', 'Unknown error')}")
        
        # Test 3: Technology Research
        logger.info("🔬 Test 3: Researching technology...")
        research_data = await research_agent.research_technology("FastAPI")
        
        if research_data and not research_data.get('error'):
            logger.success("✅ Technology research successful!")
            logger.info(f"  Technology: {research_data.get('technology')}")
            logger.info(f"  Search results: {len(research_data.get('search_results', []))}")
            logger.info(f"  Documentation sources: {len(research_data.get('documentation', []))}")
            logger.info(f"  Code examples: {len(research_data.get('code_examples', []))}")
        else:
            logger.warning(f"⚠️  Technology research failed: {research_data.get('error', 'Unknown error')}")
        
        # Test 4: Code Examples Search
        logger.info("💻 Test 4: Finding code examples...")
        code_examples = await research_agent.find_code_examples("async web scraping", "python")
        
        if code_examples:
            logger.success(f"✅ Code examples search successful! Found {len(code_examples)} examples")
            for i, example in enumerate(code_examples, 1):
                logger.info(f"  {i}. {example.get('title', 'No title')}")
                logger.info(f"     Source: {example.get('source', 'No source')}")
        else:
            logger.warning("⚠️  Code examples search returned no results")
        
        # Test 5: Task Execution Interface
        logger.info("⚙️  Test 5: Testing task execution interface...")
        
        tasks = [
            {
                "type": "web_search",
                "query": "AutoGen multi-agent framework",
                "max_results": 2
            },
            {
                "type": "research_tech",
                "technology": "Playwright"
            }
        ]
        
        for i, task in enumerate(tasks, 1):
            logger.info(f"  Executing task {i}: {task['type']}")
            result = await research_agent.execute_task(task)
            
            if result.get('status') == 'completed':
                logger.success(f"  ✅ Task {i} completed successfully")
            else:
                logger.warning(f"  ⚠️  Task {i} failed: {result.get('error', 'Unknown error')}")
        
        logger.success("🎉 All web browsing tests completed!")
        
    except Exception as e:
        logger.error(f"❌ Web browsing test failed: {e}")
        return False
    
    finally:
        # Cleanup
        await research_agent.close_browser()
        logger.info("🧹 Browser cleanup completed")
    
    return True


async def test_browser_features():
    """
    Test specific browser features and capabilities
    """
    logger.info("🎯 Testing specific browser features...")
    
    llm_config = {"config_list": [{"model": "gpt-4", "api_key": "mock"}]}
    research_agent = ResearchAgent(name="BrowserTestAgent", llm_config=llm_config)
    
    try:
        # Initialize browser
        await research_agent.initialize_browser()
        logger.success("✅ Browser initialized successfully")
        
        # Test page navigation
        if research_agent.page:
            await research_agent.page.goto("https://httpbin.org/json")
            title = await research_agent.page.title()
            content = await research_agent.page.content()
            
            logger.success(f"✅ Page navigation successful")
            logger.info(f"  Page title: {title}")
            logger.info(f"  Content length: {len(content)}")
        
        # Test JavaScript execution
        if research_agent.page:
            js_result = await research_agent.page.evaluate("() => { return {userAgent: navigator.userAgent, url: window.location.href}; }")
            logger.success("✅ JavaScript execution successful")
            logger.info(f"  User Agent: {js_result.get('userAgent', 'Unknown')[:50]}...")
            logger.info(f"  Current URL: {js_result.get('url', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"❌ Browser features test failed: {e}")
        return False
    
    finally:
        await research_agent.close_browser()
    
    return True


def main():
    """
    Main function to run all web browsing tests
    """
    logger.info("🚀 Starting AutoGen Web Browsing Tests")
    
    # Check if running in Docker or requires special setup
    if os.getenv("PLAYWRIGHT_BROWSERS_PATH"):
        logger.info(f"📂 Playwright browsers path: {os.getenv('PLAYWRIGHT_BROWSERS_PATH')}")
    
    # Run tests
    try:
        # Run basic web browsing tests
        result1 = asyncio.run(test_web_browsing())
        
        # Run browser features tests
        result2 = asyncio.run(test_browser_features())
        
        if result1 and result2:
            logger.success("🎉 All web browsing tests passed!")
            return 0
        else:
            logger.error("❌ Some tests failed")
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
    
    # Set environment for testing
    os.environ.setdefault("PLAYWRIGHT_HEADLESS", "true")
    
    exit_code = main()
    sys.exit(exit_code) 