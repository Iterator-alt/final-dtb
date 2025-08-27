"""
Google Gemini Agent Implementation

This module provides the Google Gemini-specific agent implementation for brand monitoring.
Supports both Gemini Pro and Gemini Pro Vision models with proper error handling and cost tracking.
"""

import asyncio
from typing import Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from src.agents.base_agent import BaseAgent, register_agent
from src.config.settings import LLMConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)

@register_agent("gemini")
class GeminiAgent(BaseAgent):
    """
    Google Gemini agent for brand monitoring.
    
    This agent uses Google's Gemini models to search for and analyze brand mentions
    in response to user queries with enhanced context understanding.
    """
    
    def __init__(self, name: str, config: LLMConfig):
        """Initialize the Gemini agent."""
        super().__init__(name, config)
        
        # Configure Gemini
        genai.configure(api_key=config.api_key)
        
        # Model configuration
        self.model_name = config.model or "gemini-pro"
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        
        # Initialize the generative model
        self.generation_config = genai.types.GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=0.8,
            top_k=40
        )
        
        # Safety settings - balanced for business queries
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        logger.info(f"Initialized Gemini agent with model: {self.model_name}")
    
    def _get_model_name(self) -> str:
        """Get the model name for this agent."""
        return self.model_name
    
    def _create_search_prompt(self, query: str) -> str:
        """
        Create a Gemini-optimized prompt for brand search.
        
        Args:
            query: The user's search query
            
        Returns:
            Formatted prompt optimized for Gemini models
        """
        return query
    
    async def _make_llm_request(self, query: str) -> str:
        """
        Make a request to Google Gemini API.
        
        Args:
            query: The search query to process
            
        Returns:
            Raw response from Gemini
            
        Raises:
            Exception: If the API request fails
        """
        try:
            prompt = self._create_search_prompt(query)
            
            logger.debug(f"Making Gemini request for query: {query}")
            
            # Use asyncio to run the synchronous Gemini call in a thread pool
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings
                )
            )
            
            logger.debug(f"Gemini response received: {response}")
            
            # Check if the response was blocked
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                # Check for safety blocks
                if candidate.finish_reason == 3:  # SAFETY
                    raise Exception("Response was blocked by Gemini safety filters")
                elif candidate.finish_reason == 4:  # RECITATION
                    raise Exception("Response was blocked due to recitation concerns")
                
                # Extract content
                if candidate.content and candidate.content.parts:
                    content = candidate.content.parts[0].text
                    
                    if not content or content.strip() == "":
                        # Try a simpler prompt if the first one returns empty
                        logger.warning("Empty content received, trying simpler prompt")
                        simple_response = await loop.run_in_executor(
                            None,
                            lambda: self.model.generate_content(
                                f"Provide a list of top companies and tools for: {query}. Include specific company names and brief descriptions.",
                                generation_config=genai.types.GenerationConfig(
                                    max_output_tokens=800,
                                    temperature=0.3
                                )
                            )
                        )
                        
                        if (simple_response.candidates and 
                            len(simple_response.candidates) > 0 and
                            simple_response.candidates[0].content and
                            simple_response.candidates[0].content.parts):
                            content = simple_response.candidates[0].content.parts[0].text
                        else:
                            raise Exception("Both standard and simple prompts returned empty content from Gemini")
                    
                    logger.debug(f"Gemini response length: {len(content)} characters")
                    return content.strip()
                else:
                    raise Exception("No content in Gemini response candidate")
            else:
                raise Exception("No candidates in Gemini response")
            
        except Exception as e:
            # Handle specific Gemini API errors
            error_msg = str(e)
            
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                raise Exception(f"Gemini API quota/rate limit exceeded: {error_msg}")
            elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                raise Exception(f"Gemini authentication error: {error_msg}")
            elif "safety" in error_msg.lower():
                raise Exception(f"Gemini safety filter triggered: {error_msg}")
            elif "timeout" in error_msg.lower():
                raise Exception(f"Gemini API timeout: {error_msg}")
            else:
                # For unknown errors, include the original message
                if "Gemini" not in error_msg:
                    raise Exception(f"Unexpected Gemini error: {error_msg}")
                raise
    
    def _extract_token_usage(self, response_data: Any) -> Optional[Dict[str, int]]:
        """
        Extract token usage from Gemini response.
        
        Note: Gemini API doesn't currently provide detailed token usage in responses,
        but we can estimate based on content length.
        """
        if hasattr(response_data, 'usage_metadata'):
            # Future-proofing for when Gemini adds usage metadata
            usage = response_data.usage_metadata
            return {
                'prompt_tokens': getattr(usage, 'prompt_token_count', 0),
                'completion_tokens': getattr(usage, 'candidates_token_count', 0),
                'total_tokens': getattr(usage, 'total_token_count', 0)
            }
        
        # Estimation based on content length (rough approximation)
        if hasattr(response_data, 'text'):
            content_length = len(response_data.text)
            estimated_tokens = content_length // 4  # Rough estimation: 4 chars per token
            return {
                'prompt_tokens': 0,  # Can't estimate prompt tokens without the full prompt
                'completion_tokens': estimated_tokens,
                'total_tokens': estimated_tokens
            }
        
        return None
    
    def _estimate_cost(self, token_usage: Optional[Dict[str, int]]) -> Optional[float]:
        """
        Estimate cost for Gemini API usage.
        
        Note: Prices are approximate and may change. Update regularly.
        As of 2024, Gemini Pro has different pricing tiers.
        """
        if not token_usage:
            return None
        
        # Approximate pricing for Gemini Pro (as of 2024)
        # These values should be updated based on current Google AI pricing
        if self.model_name == "gemini-pro":
            # Free tier: first 60 requests per minute are free
            # Paid tier: $0.00025 per 1K characters for input, $0.0005 per 1K characters for output
            price_per_1k_input = 0.00025
            price_per_1k_output = 0.0005
        elif self.model_name == "gemini-pro-vision":
            # Different pricing for vision model
            price_per_1k_input = 0.00025
            price_per_1k_output = 0.0005
        else:
            # Default pricing
            price_per_1k_input = 0.0001
            price_per_1k_output = 0.0002
        
        # Convert tokens to characters (approximate)
        input_chars = token_usage.get('prompt_tokens', 0) * 4
        output_chars = token_usage.get('completion_tokens', 0) * 4
        
        input_cost = (input_chars / 1000) * price_per_1k_input
        output_cost = (output_chars / 1000) * price_per_1k_output
        
        return input_cost + output_cost
    
    async def test_connection(self) -> bool:
        """
        Test the connection to Google Gemini API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            test_prompt = "Hello, this is a connection test. Please respond with 'Connection successful'."
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    test_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=50,
                        temperature=0
                    )
                )
            )
            
            return (response.candidates and 
                    len(response.candidates) > 0 and
                    response.candidates[0].content and
                    response.candidates[0].content.parts and
                    len(response.candidates[0].content.parts) > 0)
            
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            'provider': 'Google',
            'model': self.model_name,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'timeout': self.config.timeout,
            'safety_settings': str(self.safety_settings)
        }
    
    async def health_check(self) -> bool:
        """
        Perform a health check specific to Gemini.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Test with a simple business query
            test_query = "data analytics tools"
            test_prompt = f"List 3 companies that provide {test_query}."
            
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(
                        test_prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=200,
                            temperature=0.1
                        )
                    )
                ),
                timeout=15.0
            )
            
            return (response.candidates and 
                    len(response.candidates) > 0 and
                    response.candidates[0].content and
                    response.candidates[0].content.parts and
                    len(response.candidates[0].content.parts[0].text.strip()) > 10)
            
        except Exception as e:
            logger.error(f"Gemini health check failed: {str(e)}")
            return False

# Utility function for creating Gemini agents
def create_gemini_agent(name: str = "gemini", config: Dict[str, Any] = None) -> GeminiAgent:
    """
    Utility function to create a Gemini agent with configuration.
    
    Args:
        name: Name for the agent
        config: Configuration dictionary containing api_key, model, etc.
        
    Returns:
        Configured Gemini agent
    """
    from src.config.settings import get_settings
    
    settings = get_settings()
    
    # Handle both dict config and individual parameters for backward compatibility
    if isinstance(config, dict):
        # Extract values from config dictionary
        api_key = config.get("api_key", "")
        model = config.get("model", "gemini-pro")
        max_tokens = config.get("max_tokens", 1000)
        temperature = config.get("temperature", 0.1)
        timeout = config.get("timeout", 30)
    else:
        # Fallback to environment variables
        api_key = settings.gemini_api_key
        model = "gemini-pro"
        max_tokens = 1000
        temperature = 0.1
        timeout = 30
    
    # Use environment variable if config doesn't have api_key
    if not api_key:
        api_key = settings.gemini_api_key
    
    llm_config = LLMConfig(
        name=name,
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout=timeout
    )
    
    return GeminiAgent(name, llm_config)