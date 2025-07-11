import os
import asyncio
from typing import Dict, List, Any, Optional
from xai_sdk import Client
from xai_sdk.chat import user, system

class XAIClient:
    """Client for interacting with X.AI's Grok models with constitutional validation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the X.AI client with constitutional validation.
        
        Args:
            api_key: X.AI API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("X.AI API key not provided and XAI_API_KEY not found in environment")
        
        self.client = Client(
            api_host="api.x.ai",
            api_key=self.api_key
        )
        self.constitutional_hash = "cdd01ef066bc6cf2"
    
    async def chat_completion(
        self,
        message: str,
        system_prompt: str | None = None,
        model: str = "grok-4-0709",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> dict[str, Any]:
        """Send a chat completion request to Grok with constitutional validation.
        
        Args:
            message: The user message to send
            system_prompt: Optional system prompt to set context
            model: The model to use (default: grok-4-0709)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Dictionary containing the response data
            
        Raises:
            Exception: If the API call fails
        """
        try:
            # Create chat session
            chat = self.client.chat.create(
                model=model, 
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Add constitutional validation to system prompt
            constitutional_system = f"Constitutional Hash: {self.constitutional_hash}\n"
            if system_prompt:
                constitutional_system += system_prompt
            else:
                constitutional_system += "You are a helpful AI assistant."
            
            # Add messages
            chat.append(system(constitutional_system))
            chat.append(user(message))
            
            # Get response
            response = chat.sample()
            
            # Extract and return response data
            return {
                "success": True,
                "content": response.content,
                "model": model,
                "constitutional_hash_valid": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "constitutional_hash_valid": False
            }

async def test_xai_integration():
    """Test the X.AI integration with constitutional validation."""
    try:
        # Initialize the client
        print("📡 Initializing X.AI API client...")
        client = XAIClient()
        print(f"✅ Client initialized with constitutional hash: {client.constitutional_hash}")

        # Test message
        test_message = """
        Explain the concept of constitutional AI governance in simple terms,
        including its importance for responsible AI deployment.
        """

        system_prompt = """
        You are a helpful AI assistant that explains complex topics clearly and concisely.
        Focus on making technical concepts accessible to a general audience.
        Always adhere to constitutional governance principles.
        """

        print("\n💬 Sending test message...")
        print(f"Message: {test_message.strip()}")

        # Make the API call
        result = await client.chat_completion(
            message=test_message,
            system_prompt=system_prompt,
            temperature=0.7,
        )

        if result["success"]:
            print("\n✅ Successfully received response:")
            print(f"Constitutional Hash Valid: {result['constitutional_hash_valid']}")
            print(f"Model: {result['model']}")
            print(f"Response: {result['content'][:200]}...")
            return True
        else:
            print(f"\n❌ Error: {result['error']}")
            return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_xai_integration())