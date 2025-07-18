"""
Chat Agent - AI-powered dialogue assistant with constitutional compliance
Constitutional Hash: cdd01ef066bc6cf2
"""

import openai
import anthropic
import logging
import time
from typing import Dict, List, Optional, AsyncGenerator
import asyncio
import json

from ..models.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationMessage,
    MessageRole,
    ComplianceLevel,
    CONSTITUTIONAL_HASH,
)
from ..services.conversation_manager import ConversationManager
from ..services.compliance_checker import ComplianceChecker

logger = logging.getLogger(__name__)


class ChatAgent:
    """
    AI-powered chat agent with multi-provider support and constitutional compliance.
    Supports OpenAI, Anthropic, and local models with conversation context management.
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        redis_url: str = "redis://localhost:6379/0",
    ):
        """Initialize chat agent with AI providers and services."""
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Initialize AI providers
        self.openai_client = None
        self.anthropic_client = None

        if openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)

        if anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)

        # Initialize services
        self.conversation_manager = ConversationManager(redis_url)
        self.compliance_checker = ComplianceChecker()

        # Default model preferences
        self.default_model = "gpt-3.5-turbo"
        self.model_preferences = {
            "openai": ["gpt-4", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "fallback": "mock",
        }

        # System prompt for constitutional compliance
        self.system_prompt = """You are a helpful AI assistant that operates under strict constitutional compliance guidelines. 

Constitutional Hash: cdd01ef066bc6cf2

You must:
1. Provide accurate, helpful, and respectful responses
2. Respect user privacy and confidentiality
3. Avoid harmful, illegal, or inappropriate content
4. Maintain constitutional compliance in all interactions
5. Be transparent about your capabilities and limitations

You should be conversational, engaging, and supportive while maintaining these principles."""

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process chat request with constitutional compliance validation.

        Args:
            request: Chat request with message and context

        Returns:
            ChatResponse with AI-generated response and compliance check
        """
        start_time = time.time()

        try:
            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                raise ValueError(
                    f"Constitutional hash mismatch: {request.constitutional_hash}"
                )

            # Check input compliance
            input_compliance = await self.compliance_checker.check_message_compliance(
                request.message, MessageRole.USER, request.compliance_level
            )

            if not input_compliance.compliant:
                return ChatResponse(
                    response="I cannot process this message due to compliance violations. Please revise your request.",
                    conversation_id=request.conversation_id or "unknown",
                    message_id="compliance_error",
                    compliance_check=input_compliance.dict(),
                    constitutional_hash=self.constitutional_hash,
                )

            # Get or create conversation context
            context = await self._get_conversation_context(request)

            # Generate AI response
            ai_response = await self._generate_response(request, context)

            # Check output compliance
            output_compliance = await self.compliance_checker.check_message_compliance(
                ai_response, MessageRole.ASSISTANT, request.compliance_level
            )

            # If not compliant, generate safer response
            if not output_compliance.compliant:
                ai_response = await self._generate_safe_response(request, context)
                output_compliance = (
                    await self.compliance_checker.check_message_compliance(
                        ai_response, MessageRole.ASSISTANT, request.compliance_level
                    )
                )

            # Store conversation messages
            await self._store_conversation_messages(request, ai_response, context)

            processing_time = (time.time() - start_time) * 1000

            return ChatResponse(
                response=ai_response,
                conversation_id=context.conversation_id,
                message_id=f"msg_{int(time.time())}",
                compliance_check=output_compliance.dict(),
                usage={"total_tokens": len(ai_response.split())},  # Approximate
                metadata={
                    "model": self.default_model,
                    "compliance_level": request.compliance_level.value,
                    "processing_time_ms": processing_time,
                },
                constitutional_hash=self.constitutional_hash,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return ChatResponse(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                conversation_id=request.conversation_id or "error",
                message_id="error",
                compliance_check={"error": str(e)},
                constitutional_hash=self.constitutional_hash,
            )

    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """
        Process chat request with streaming response.

        Args:
            request: Chat request with streaming enabled

        Yields:
            Response chunks as they are generated
        """
        try:
            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                yield json.dumps({"error": "Constitutional hash mismatch"})
                return

            # Check input compliance
            input_compliance = await self.compliance_checker.check_message_compliance(
                request.message, MessageRole.USER, request.compliance_level
            )

            if not input_compliance.compliant:
                yield json.dumps(
                    {
                        "chunk": "I cannot process this message due to compliance violations.",
                        "conversation_id": request.conversation_id or "unknown",
                        "is_final": True,
                    }
                )
                return

            # Get conversation context
            context = await self._get_conversation_context(request)

            # Generate streaming response
            full_response = ""
            async for chunk in self._generate_streaming_response(request, context):
                full_response += chunk
                yield json.dumps(
                    {
                        "chunk": chunk,
                        "conversation_id": context.conversation_id,
                        "is_final": False,
                        "constitutional_hash": self.constitutional_hash,
                    }
                )

            # Final compliance check
            output_compliance = await self.compliance_checker.check_message_compliance(
                full_response, MessageRole.ASSISTANT, request.compliance_level
            )

            # Store conversation
            await self._store_conversation_messages(request, full_response, context)

            # Send final chunk
            yield json.dumps(
                {
                    "chunk": "",
                    "conversation_id": context.conversation_id,
                    "is_final": True,
                    "compliance_check": output_compliance.dict(),
                    "constitutional_hash": self.constitutional_hash,
                }
            )

        except Exception as e:
            logger.error(f"Streaming chat failed: {e}")
            yield json.dumps(
                {"error": str(e), "constitutional_hash": self.constitutional_hash}
            )

    async def _get_conversation_context(self, request: ChatRequest):
        """Get or create conversation context."""
        if request.conversation_id:
            conversation = await self.conversation_manager.get_conversation(
                request.conversation_id
            )
            if conversation:
                return conversation.context

        # Create new conversation context
        from ..models.schemas import ConversationContext
        import uuid

        context = ConversationContext(
            user_id=request.context.user_id if request.context else "anonymous",
            session_id=(
                request.context.session_id if request.context else str(uuid.uuid4())
            ),
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            constitutional_hash=self.constitutional_hash,
        )

        # Create conversation
        await self.conversation_manager.create_conversation(context)

        return context

    async def _generate_response(self, request: ChatRequest, context) -> str:
        """Generate AI response using available providers."""
        try:
            # Get conversation history
            conversation_history = (
                await self.conversation_manager.get_conversation_context(
                    context.conversation_id
                )
            )

            # Prepare messages
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": request.message})

            # Try OpenAI first
            if self.openai_client:
                response = await self._generate_openai_response(messages, request)
                if response:
                    return response

            # Try Anthropic
            if self.anthropic_client:
                response = await self._generate_anthropic_response(messages, request)
                if response:
                    return response

            # Fallback to mock response
            return self._generate_mock_response(request.message)

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."

    async def _generate_openai_response(
        self, messages: List[Dict], request: ChatRequest
    ) -> Optional[str]:
        """Generate response using OpenAI API."""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=False,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return None

    async def _generate_anthropic_response(
        self, messages: List[Dict], request: ChatRequest
    ) -> Optional[str]:
        """Generate response using Anthropic API."""
        try:
            # Convert messages to Anthropic format
            system_msg = (
                messages[0]["content"] if messages[0]["role"] == "system" else ""
            )
            user_messages = [msg for msg in messages[1:] if msg["role"] != "system"]

            response = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_msg,
                messages=user_messages,
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            return None

    def _generate_mock_response(self, message: str) -> str:
        """Generate mock response for testing."""
        responses = [
            f"Thank you for your message: '{message[:50]}...' I'm here to help!",
            "I understand your question. Let me provide a helpful response.",
            "That's an interesting point. I'd be happy to assist you with that.",
            "I appreciate your question and will do my best to provide a useful answer.",
        ]

        import random

        return random.choice(responses)

    async def _generate_streaming_response(
        self, request: ChatRequest, context
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        try:
            # Get conversation history
            conversation_history = (
                await self.conversation_manager.get_conversation_context(
                    context.conversation_id
                )
            )

            # Prepare messages
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": request.message})

            # Try OpenAI streaming
            if self.openai_client:
                async for chunk in self._stream_openai_response(messages, request):
                    yield chunk
                return

            # Fallback to mock streaming
            mock_response = self._generate_mock_response(request.message)
            for word in mock_response.split():
                yield word + " "
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield "I apologize, but I'm having trouble with streaming right now."

    async def _stream_openai_response(
        self, messages: List[Dict], request: ChatRequest
    ) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI."""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=True,
            )

            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            yield "Streaming error occurred."

    async def _generate_safe_response(self, request: ChatRequest, context) -> str:
        """Generate a safer response when compliance fails."""
        safe_responses = [
            "I understand your question, but I need to provide a response that maintains appropriate standards. Could you please rephrase your request?",
            "I'd be happy to help, but I need to ensure my response follows proper guidelines. Could you provide more context or ask in a different way?",
            "I want to be helpful while maintaining appropriate standards. Could you clarify what specific information you're looking for?",
            "I'm here to assist, but I need to ensure my responses are appropriate and helpful. Could you please rephrase your question?",
        ]

        import random

        return random.choice(safe_responses)

    async def _store_conversation_messages(
        self, request: ChatRequest, response: str, context
    ):
        """Store conversation messages."""
        try:
            # Store user message
            user_message = ConversationMessage(
                role=MessageRole.USER, content=request.message, compliance_checked=True
            )
            await self.conversation_manager.add_message(
                context.conversation_id, user_message
            )

            # Store assistant response
            assistant_message = ConversationMessage(
                role=MessageRole.ASSISTANT, content=response, compliance_checked=True
            )
            await self.conversation_manager.add_message(
                context.conversation_id, assistant_message
            )

        except Exception as e:
            logger.error(f"Failed to store conversation messages: {e}")
