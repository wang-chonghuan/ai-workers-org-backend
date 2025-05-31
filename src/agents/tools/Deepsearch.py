import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()


class Deepsearch:
    """
    A simple wrapper for Perplexity API to perform deep search queries.
    """
    
    def __init__(self):
        """Initialize the Deepsearch client with Perplexity API."""
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables")
        
        # Initialize OpenAI client with Perplexity API base URL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai"
        )
    
    def search(self, query: str, model: str = "sonar-pro", 
               system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a search query using Perplexity API.
        
        Args:
            query (str): The search query to execute
            model (str): The model to use for the search. Available models:
                        - sonar-pro [default] (Latest premium model)
                        Online models (with web search):
                        - llama-3.1-sonar-small-128k-online (8B)
                        - llama-3.1-sonar-large-128k-online (70B)
                        - llama-3.1-sonar-huge-128k-online (405B)
                        Chat models (offline):
                        - llama-3.1-sonar-small-128k-chat (8B)
                        - llama-3.1-sonar-large-128k-chat (70B)
            system_prompt (str, optional): Custom system prompt for the search
        
        Returns:
            Dict[str, Any]: The response from Perplexity API
        """
        # Default system prompt if none provided
        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant that provides accurate, "
                "up-to-date information based on web search results. "
                "Please provide detailed and factual responses."
            )
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": query
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model,
                "usage": response.usage.model_dump() if response.usage else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def search_streaming(self, query: str, model: str = "sonar-pro",
                        system_prompt: Optional[str] = None):
        """
        Perform a streaming search query using Perplexity API.
        
        Args:
            query (str): The search query to execute
            model (str): The model to use for the search. Available models:
                        - sonar-pro [default] (Latest premium model)
                        Online models (with web search):
                        - llama-3.1-sonar-small-128k-online (8B)
                        - llama-3.1-sonar-large-128k-online (70B)
                        - llama-3.1-sonar-huge-128k-online (405B)
                        Chat models (offline):
                        - llama-3.1-sonar-small-128k-chat (8B)
                        - llama-3.1-sonar-large-128k-chat (70B)
            system_prompt (str, optional): Custom system prompt for the search
        
        Yields:
            Dict[str, Any]: Streaming response chunks from Perplexity API
        """
        # Default system prompt if none provided
        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant that provides accurate, "
                "up-to-date information based on web search results. "
                "Please provide detailed and factual responses."
            )
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        try:
            response_stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    yield {
                        "success": True,
                        "content": chunk.choices[0].delta.content,
                        "finished": False
                    }
            
            yield {"success": True, "content": "", "finished": True}
            
        except Exception as e:
            yield {
                "success": False,
                "error": str(e),
                "content": None,
                "finished": True
            }


# Example usage
if __name__ == "__main__":
    # Initialize the Deepsearch instance
    searcher = Deepsearch()
    
    # Example search query using OpenAI client
    print("=== Using OpenAI Client Method ===")
    result = searcher.search("What are the latest developments in AI technology?")
    
    if result["success"]:
        print("Search Result:")
        print(result["content"])
        if result.get("usage"):
            print(f"Usage: {result['usage']}")
    else:
        print(f"Error: {result['error']}")
    
    print("\n" + "="*50 + "\n")
    
    # Example streaming search
    print("=== Using Streaming Method ===")
    print("Streaming Result:")
    for chunk in searcher.search_streaming("What are the latest developments in AI technology?"):
        if chunk["success"] and not chunk["finished"]:
            print(chunk["content"], end="", flush=True)
        elif chunk["finished"]:
            print("\n[Streaming completed]")
        else:
            print(f"Error: {chunk['error']}")
            break
