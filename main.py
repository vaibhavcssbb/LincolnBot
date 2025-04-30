import os
import logging
from dotenv import load_dotenv
from search_engine import SearchEngine
from response_generator import ResponseGenerator
from response_validator import ResponseValidator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'app.log')
)
logger = logging.getLogger(__name__)

class LincolnBot:
    def __init__(self):
        """Initialize the LincolnBot with all required components."""
        self.search_engine = SearchEngine()
        self.response_generator = ResponseGenerator()
        self.response_validator = ResponseValidator()
        logger.info("LincolnBot initialized successfully")

    def process_query(self, query: str) -> dict:
        """
        Process a user query and return a response.
        
        Args:
            query: The user's query string
            
        Returns:
            Dictionary containing the response and validation results
        """
        try:
            # Perform search
            search_results = self.search_engine.search(query)
            logger.info(f"Search completed for query: {query}")
            
            # Generate response
            response = self.response_generator.generate_response(query, search_results)
            logger.info(f"Response generated for query: {query}")
            
            # Validate response
            validation_result = self.response_validator.validate_response(query, response)
            logger.info(f"Response validated for query: {query}")
            
            # Combine results
            result = {
                'query': query,
                'response': response,
                'validation': validation_result
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'query': query,
                'error': str(e),
                'response': None,
                'validation': None
            }

def main():
    """Main function to run the LincolnBot application."""
    try:
        # Initialize the bot
        bot = LincolnBot()
        
        # Example queries
        test_queries = [
            "What are the parking permit requirements?",
            "How much does a resident parking permit cost?",
            "What are the penalties for parking violations?"
        ]
        
        # Process each query
        for query in test_queries:
            print(f"\nProcessing query: {query}")
            result = bot.process_query(query)
            
            if result.get('error'):
                print(f"Error: {result['error']}")
            else:
                print("\nResponse:")
                print(result['response']['answer'])
                print("\nSources:")
                for source in result['response']['sources']:
                    print(f"- {source['text']} (Score: {source['score']})")
                print("\nValidation:")
                print(f"Valid: {result['validation']['is_valid']}")
                if not result['validation']['is_valid']:
                    print("Issues:")
                    for issue in result['validation']['issues']:
                        print(f"- {issue}")
                    if result['validation']['missing_fields']:
                        print("Missing fields:")
                        for field in result['validation']['missing_fields']:
                            print(f"- {field}")
                    if result['validation']['inconsistencies']:
                        print("Inconsistencies:")
                        for inconsistency in result['validation']['inconsistencies']:
                            print(f"- {inconsistency}")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 