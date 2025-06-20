"""
Foundation model integration for DGM Service.

Provides secure integration with various foundation models including
Claude 3.5 Sonnet, GPT-4, and other LLMs for improvement generation
and analysis.
"""

from .model_client import ModelClient
from .claude_client import ClaudeClient
from .openai_client import OpenAIClient
from .model_router import ModelRouter

__all__ = [
    "ModelClient",
    "ClaudeClient", 
    "OpenAIClient",
    "ModelRouter"
]
