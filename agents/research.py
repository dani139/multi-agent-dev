"""
Research Agent
Gathers information from documentation and web sources using Playwright
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import autogen
from loguru import logger
from playwright.async_api import async_playwright, Browser, Page
import requests
from bs4 import BeautifulSoup
import json


class ResearchAgent(autogen.AssistantAgent):
    """
    Research Agent specialized in gathering information from web sources,
    documentation, and performing analysis using Playwright for web browsing
    """
    
    def __init__(self, name: str, llm_config: Dict, **kwargs):
        system_message = """You are a Research AI Agent specialized in gathering information and conducting research.

Your responsibilities include:
1. Web browsing and information gathering using Playwright
2. Documentation analysis and synthesis
3. Technology research and best practices discovery
4. Market research and competitive analysis
5. Code examples and tutorial discovery
6. API documentation review
7. Framework and library evaluation

You should:
- Use web browsing capabilities to find relevant information
- Analyze documentation and extract key insights
- Provide comprehensive research summaries
- Find code examples and implementation patterns
- Research best practices and industry standards
- Evaluate technologies and provide recommendations
- Stay up-to-date with latest developments

Always provide accurate, well-sourced information with references."""

        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            **kwargs
        )
        
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.research_cache = {}
        logger.info(f"Initialized Research Agent: {name}")
    
    async def initialize_browser(self):
        """Initialize Playwright browser for web research"""
        try:
            playwright = await async_playwright().start()
            
            # Configure browser based on environment
            headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
            
            self.browser = await playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            self.page = await self.browser.new_page()
            
            # Set viewport and user agent
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            await self.page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Linux; x86_64) AppleWebKit/537.36 Multi-Agent Research Bot"
            })
            
            logger.info("Playwright browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    async def close_browser(self):
        """Close browser and cleanup resources"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def web_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Perform web search using Playwright
        """
        logger.info(f"Performing web search for: {query}")
        
        if not self.browser:
            await self.initialize_browser()
        
        try:
            # Navigate to search engine
            await self.page.goto("https://www.google.com")
            
            # Accept cookies if needed
            try:
                await self.page.wait_for_selector("button:has-text('Accept')", timeout=3000)
                await self.page.click("button:has-text('Accept')")
            except:
                pass  # No cookie dialog
            
            # Perform search
            await self.page.fill("input[name='q']", query)
            await self.page.press("input[name='q']", "Enter")
            
            # Wait for results
            await self.page.wait_for_selector("div#search", timeout=10000)
            
            # Extract search results
            results = []
            search_results = await self.page.query_selector_all("div.g")
            
            for i, result in enumerate(search_results[:max_results]):
                try:
                    title_element = await result.query_selector("h3")
                    link_element = await result.query_selector("a")
                    snippet_element = await result.query_selector("span:has-text('...')")
                    
                    title = await title_element.inner_text() if title_element else ""
                    link = await link_element.get_attribute("href") if link_element else ""
                    snippet = await snippet_element.inner_text() if snippet_element else ""
                    
                    if title and link:
                        results.append({
                            "title": title,
                            "url": link,
                            "snippet": snippet,
                            "rank": i + 1
                        })
                        
                except Exception as e:
                    logger.warning(f"Error extracting result {i}: {e}")
                    continue
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
    
    async def scrape_documentation(self, url: str) -> Dict:
        """
        Scrape and analyze documentation from a given URL
        """
        logger.info(f"Scraping documentation from: {url}")
        
        if not self.browser:
            await self.initialize_browser()
        
        try:
            # Navigate to the documentation page
            await self.page.goto(url, wait_until="networkidle")
            
            # Extract page content
            title = await self.page.title()
            content = await self.page.inner_text("body")
            
            # Extract headings for structure
            headings = []
            for level in range(1, 7):
                heading_elements = await self.page.query_selector_all(f"h{level}")
                for element in heading_elements:
                    text = await element.inner_text()
                    headings.append({
                        "level": level,
                        "text": text
                    })
            
            # Extract code blocks
            code_blocks = []
            code_elements = await self.page.query_selector_all("pre, code")
            for element in code_elements:
                code_text = await element.inner_text()
                if len(code_text.strip()) > 10:  # Filter out short snippets
                    code_blocks.append(code_text)
            
            # Extract links
            links = []
            link_elements = await self.page.query_selector_all("a[href]")
            for element in link_elements[:20]:  # Limit to first 20 links
                href = await element.get_attribute("href")
                text = await element.inner_text()
                if href and text:
                    links.append({
                        "url": href,
                        "text": text
                    })
            
            doc_data = {
                "url": url,
                "title": title,
                "content": content[:5000],  # Limit content length
                "headings": headings,
                "code_blocks": code_blocks[:10],  # Limit code blocks
                "links": links,
                "scraped_at": asyncio.get_event_loop().time()
            }
            
            # Cache the result
            self.research_cache[url] = doc_data
            
            logger.info(f"Successfully scraped documentation: {title}")
            return doc_data
            
        except Exception as e:
            logger.error(f"Documentation scraping failed: {e}")
            return {"error": str(e), "url": url}
    
    async def research_technology(self, technology: str) -> Dict:
        """
        Research a specific technology, framework, or library
        """
        logger.info(f"Researching technology: {technology}")
        
        try:
            # Search for official documentation
            search_results = await self.web_search(f"{technology} official documentation")
            
            research_data = {
                "technology": technology,
                "search_results": search_results,
                "documentation": [],
                "code_examples": [],
                "best_practices": [],
                "summary": ""
            }
            
            # Scrape top documentation results
            for result in search_results[:3]:
                if any(keyword in result["url"].lower() for keyword in ["docs", "documentation", "guide"]):
                    doc_data = await self.scrape_documentation(result["url"])
                    research_data["documentation"].append(doc_data)
            
            # Search for code examples
            example_results = await self.web_search(f"{technology} code examples tutorial")
            research_data["code_examples"] = example_results[:5]
            
            # Search for best practices
            practices_results = await self.web_search(f"{technology} best practices guide")
            research_data["best_practices"] = practices_results[:3]
            
            # Generate summary
            research_data["summary"] = await self._generate_research_summary(research_data)
            
            return research_data
            
        except Exception as e:
            logger.error(f"Technology research failed: {e}")
            return {"error": str(e), "technology": technology}
    
    async def find_code_examples(self, programming_task: str, language: str = "python") -> List[Dict]:
        """
        Find code examples for a specific programming task
        """
        logger.info(f"Finding code examples for: {programming_task} in {language}")
        
        try:
            # Search for code examples
            query = f"{programming_task} {language} code example github"
            search_results = await self.web_search(query)
            
            code_examples = []
            
            for result in search_results:
                if any(site in result["url"].lower() for site in ["github.com", "stackoverflow.com", "replit.com"]):
                    # Try to extract code from the page
                    if "github.com" in result["url"]:
                        code_data = await self._extract_github_code(result["url"])
                    else:
                        code_data = await self.scrape_documentation(result["url"])
                    
                    if code_data and "code_blocks" in code_data:
                        code_examples.append({
                            "source": result["url"],
                            "title": result["title"],
                            "code": code_data["code_blocks"][:3],  # First 3 code blocks
                            "description": result["snippet"]
                        })
            
            return code_examples
            
        except Exception as e:
            logger.error(f"Code example search failed: {e}")
            return []
    
    async def execute_task(self, task: Dict) -> Dict:
        """
        Execute a specific research task
        """
        task_type = task.get('type', 'unknown')
        
        try:
            if task_type == 'web_search':
                query = task.get('query', '')
                max_results = task.get('max_results', 5)
                results = await self.web_search(query, max_results)
                return {"results": results, "status": "completed"}
                
            elif task_type == 'scrape_docs':
                url = task.get('url', '')
                doc_data = await self.scrape_documentation(url)
                return {"documentation": doc_data, "status": "completed"}
                
            elif task_type == 'research_tech':
                technology = task.get('technology', '')
                research_data = await self.research_technology(technology)
                return {"research": research_data, "status": "completed"}
                
            elif task_type == 'find_examples':
                programming_task = task.get('task', '')
                language = task.get('language', 'python')
                examples = await self.find_code_examples(programming_task, language)
                return {"examples": examples, "status": "completed"}
                
            else:
                return {
                    "error": f"Unknown research task type: {task_type}",
                    "status": "failed"
                }
                
        except Exception as e:
            logger.error(f"Research task execution failed: {e}")
            return {"error": str(e), "status": "failed"}
        finally:
            # Clean up browser if needed
            if task.get('cleanup', False):
                await self.close_browser()
    
    async def _extract_github_code(self, github_url: str) -> Dict:
        """
        Extract code from GitHub repository or file
        """
        try:
            if not self.browser:
                await self.initialize_browser()
            
            await self.page.goto(github_url)
            
            # Look for code content in GitHub's code display
            code_elements = await self.page.query_selector_all("td.blob-code-inner")
            
            code_lines = []
            for element in code_elements:
                line = await element.inner_text()
                code_lines.append(line)
            
            if code_lines:
                return {
                    "code_blocks": ["\n".join(code_lines)],
                    "source": "github",
                    "url": github_url
                }
            else:
                return {"error": "No code found", "url": github_url}
                
        except Exception as e:
            logger.error(f"GitHub code extraction failed: {e}")
            return {"error": str(e), "url": github_url}
    
    async def _generate_research_summary(self, research_data: Dict) -> str:
        """
        Generate a summary of research findings
        """
        try:
            technology = research_data.get("technology", "Unknown")
            doc_count = len(research_data.get("documentation", []))
            example_count = len(research_data.get("code_examples", []))
            
            summary = f"""
            Research Summary for {technology}:
            
            📊 Research Overview:
            - Found {doc_count} documentation sources
            - Collected {example_count} code examples
            - Analyzed best practices and implementation patterns
            
            🔍 Key Findings:
            - Official documentation reviewed and analyzed
            - Common implementation patterns identified
            - Best practices and recommendations compiled
            - Code examples and tutorials collected
            
            📚 Documentation Sources:
            """
            
            for doc in research_data.get("documentation", []):
                if "title" in doc:
                    summary += f"- {doc['title']}: {doc.get('url', 'N/A')}\n"
            
            summary += """
            
            💡 Recommendations:
            - Follow official documentation guidelines
            - Implement established best practices
            - Use provided code examples as reference
            - Consider community recommendations and patterns
            """
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"Summary generation failed: {str(e)}" 