import os
from typing import List, Dict, Any
import openai
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResponseGenerator:
    def __init__(self):
        """Initialize the response generator with required components."""
        # Initialize OpenAI client
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Load configuration
        self.max_tokens = int(os.getenv('MAX_TOKENS', 1000))
        self.temperature = float(os.getenv('TEMPERATURE', 0.7))
        self.model_name = os.getenv('MODEL_NAME', 'gpt-4-turbo-preview')
        
        logger.info("Response generator initialized successfully")

    def generate_response(self, query: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a natural language response based on search results.
        
        Args:
            query: The user's query
            search_results: List of search results with text and metadata
            
        Returns:
            Dictionary containing the generated response and source information
        """
        try:
            # Prepare context from search results
            context = "\n\n".join([
                f"Source: {result['metadata']['source']}\n"
                f"Page: {result['metadata'].get('page', 'N/A')}\n"
                f"Content: {result['text']}"
                for result in search_results
            ])
            
            # Prepare system message
            system_message = """You are an AI assistant that helps users find information about parking rules, 
            permits, and penalties in Lincoln City. Your responses should be:
            1. Accurate and based only on the provided context
            2. Clear and concise
            3. Include relevant source information
            4. Address the user's specific query"""
            
            # Generate response using OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Query: {query}\n\nContext:\n{context}"}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract the generated response
            answer = response.choices[0].message.content
            
            # Format the response
            formatted_response = {
                'answer': answer,
                'sources': search_results
            }
            
            logger.info(f"Generated response for query: {query}")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                'answer': "I apologize, but I encountered an error while processing your request. Please try again later.",
                'sources': []
            } 