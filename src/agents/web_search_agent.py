#!/usr/bin/env python3
"""
Web Search Agent for enhanced brand monitoring.
"""

import asyncio
import aiohttp
import re
from typing import List, Dict, Optional
from src.agents.base_agent import BaseAgent
from src.workflow.state import AgentResult
from src.utils.brand_detector import EnhancedBrandDetector
from src.config.settings import get_settings

class WebSearchAgent(BaseAgent):
    """Web search agent that can scrape web pages for brand information."""
    
    def __init__(self, name: str, config):
        """Initialize the web search agent."""
        super().__init__(name, config)
        self.settings = get_settings()
        self.brand_detector = EnhancedBrandDetector(self.settings.brand)
        
    async def execute(self, query: str) -> AgentResult:
        """Execute web search for the given query."""
        try:
            # Search for DataTobiz specifically
            search_queries = [
                f"DataTobiz Power BI India",
                f"DataTobiz data analytics company India",
                f"DataTobiz business intelligence services",
                f"DataTobiz consulting India"
            ]
            
            all_content = []
            
            for search_query in search_queries:
                content = await self._search_web(search_query)
                if content:
                    all_content.append(content)
            
            # Combine all content
            combined_content = " ".join(all_content)
            
            # Detect brand in the combined content
            brand_result = self.brand_detector.detect_brand(combined_content, include_ranking=False)
            
            return AgentResult(
                agent_name=self.name,
                query=query,
                response=combined_content[:1000] if combined_content else "No web content found",
                brand_found=brand_result.found,
                confidence=brand_result.confidence,
                matches=brand_result.matches,
                context=brand_result.context,
                ranking_position=None,
                ranking_context=None,
                cost=0.0,
                execution_time=0.0
            )
            
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                query=query,
                response=f"Error: {str(e)}",
                brand_found=False,
                confidence=0.0,
                matches=[],
                context="",
                ranking_position=None,
                ranking_context=None,
                cost=0.0,
                execution_time=0.0
            )
    
    async def _search_web(self, query: str) -> Optional[str]:
        """Search the web for the given query."""
        try:
            # Use a simple web search approach
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Extract text content (simplified)
                        text_content = re.sub(r'<[^>]+>', '', content)
                        return text_content[:2000]  # Limit content length
                    else:
                        return None
                        
        except Exception as e:
            print(f"Web search error: {str(e)}")
            return None
    
    async def test_connection(self) -> bool:
        """Test if the web search agent can connect."""
        try:
            # Simple connection test
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.google.com", timeout=10) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def cleanup(self):
        """Cleanup resources."""
        pass

def create_web_search_agent(name: str, config) -> WebSearchAgent:
    """Factory function to create a web search agent."""
    return WebSearchAgent(name, config)
