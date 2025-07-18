"""
Advanced Chat Agent - Claude 3.5 Sonnet support with voice integration
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import asyncio
import os
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
import json
import io
import base64
import speech_recognition as sr
import pyttsx3
import webrtcvad
import pyaudio
import wave
import numpy as np
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModel, pipeline
import torch
import tiktoken
import redis.asyncio as redis

from ..models.schemas import (
    ChatMessage,
    ChatResponse,
    ConversationContext,
    VoiceMessage,
    MessageType,
    LLMProvider,
    CONSTITUTIONAL_HASH,
)

logger = logging.getLogger(__name__)


class AdvancedChatAgent:
    """Advanced chat agent with Claude 3.5 Sonnet and voice capabilities."""

    def __init__(self, redis_url: str = "redis://localhost:6389"):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_client = None
        self.redis_url = redis_url

        # Voice components
        self.speech_recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2

        # LLM configurations
        self.llm_configs = {
            LLMProvider.ANTHROPIC: {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4000,
                "temperature": 0.7,
            },
            LLMProvider.OPENAI: {
                "model": "gpt-4o",
                "max_tokens": 4000,
                "temperature": 0.7,
            },
        }

        # Initialize services
        self._initialize_services()

    def _initialize_services(self):
        """Initialize all chat services."""
        try:
            logger.info("Initializing advanced chat services...")

            # Initialize LLM providers
            self.llm_providers = {
                LLMProvider.ANTHROPIC: ChatAnthropic(
                    model=self.llm_configs[LLMProvider.ANTHROPIC]["model"],
                    max_tokens=self.llm_configs[LLMProvider.ANTHROPIC]["max_tokens"],
                    temperature=self.llm_configs[LLMProvider.ANTHROPIC]["temperature"],
                    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                ),
                LLMProvider.OPENAI: ChatOpenAI(
                    model=self.llm_configs[LLMProvider.OPENAI]["model"],
                    max_tokens=self.llm_configs[LLMProvider.OPENAI]["max_tokens"],
                    temperature=self.llm_configs[LLMProvider.OPENAI]["temperature"],
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                ),
            }

            # Initialize conversation chains with summarization
            self.conversation_chains = {}
            for provider, llm in self.llm_providers.items():
                memory = ConversationSummaryBufferMemory(
                    llm=llm, max_token_limit=2000, return_messages=True
                )

                self.conversation_chains[provider] = ConversationChain(
                    llm=llm, memory=memory, verbose=True
                )

            # Initialize constitutional compliance checker
            self.compliance_model = AutoModel.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            self.compliance_tokenizer = AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )

            # Initialize text summarizer for long conversations
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1,
            )

            # Configure TTS
            self.tts_engine.setProperty("rate", 150)
            self.tts_engine.setProperty("volume", 0.8)

            logger.info("Advanced chat services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize chat services: {e}")
            raise

    async def initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            raise

    async def process_message_advanced(
        self,
        message: ChatMessage,
        context: ConversationContext,
        provider: LLMProvider = LLMProvider.ANTHROPIC,
    ) -> ChatResponse:
        """Process message with advanced capabilities."""
        try:
            # Multi-model consensus for important queries
            if context.enable_consensus and message.importance == "high":
                return await self._process_with_consensus(message, context)

            # Single model processing
            response = await self._process_single_model(message, context, provider)

            # Post-processing enhancements
            if context.enable_analysis:
                response = await self._enhance_response(response, context)

            return response

        except Exception as e:
            logger.error(f"Advanced message processing failed: {e}")
            raise

    async def _process_with_consensus(
        self, message: ChatMessage, context: ConversationContext
    ) -> ChatResponse:
        """Process message with multi-model consensus."""
        try:
            # Get responses from multiple models
            tasks = []
            for provider in [LLMProvider.ANTHROPIC, LLMProvider.OPENAI]:
                if provider in self.llm_providers:
                    tasks.append(self._process_single_model(message, context, provider))

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter successful responses
            valid_responses = [r for r in responses if not isinstance(r, Exception)]

            if not valid_responses:
                raise Exception("All models failed to generate response")

            # Consensus logic - use majority voting or highest confidence
            if len(valid_responses) == 1:
                return valid_responses[0]

            # Simple consensus: choose highest confidence
            best_response = max(valid_responses, key=lambda r: r.confidence)

            # Enhance with consensus metadata
            best_response.metadata["consensus"] = {
                "models_used": len(valid_responses),
                "consensus_confidence": best_response.confidence,
                "alternative_responses": len(valid_responses) - 1,
            }

            return best_response

        except Exception as e:
            logger.error(f"Consensus processing failed: {e}")
            raise

    async def _process_single_model(
        self, message: ChatMessage, context: ConversationContext, provider: LLMProvider
    ) -> ChatResponse:
        """Process message with single model."""
        try:
            # Load conversation history
            history = await self._load_conversation_history(context.conversation_id)

            # Context summarization for long conversations
            if len(history) > 10:
                summary = await self._summarize_conversation(history)
                # Update context with summary
                context.summary = summary

            # Constitutional compliance check
            compliance_result = await self._check_message_compliance(message)
            if not compliance_result["compliant"]:
                return ChatResponse(
                    message_id=message.id,
                    content=f"I cannot process this message due to constitutional compliance concerns: {compliance_result['reason']}",
                    message_type=MessageType.ERROR,
                    confidence=0.0,
                    provider=provider,
                    constitutional_hash=self.constitutional_hash,
                )

            # Enhanced prompt with constitutional context
            enhanced_prompt = await self._create_enhanced_prompt(message, context)

            # Generate response
            chain = self.conversation_chains[provider]

            # Add constitutional system message
            system_message = SystemMessage(
                content=f"""
            You are a constitutional AI assistant operating under hash {self.constitutional_hash}.
            Always prioritize:
            1. Human dignity and rights
            2. Truthfulness and accuracy
            3. Helpfulness while avoiding harm
            4. Respect for privacy and autonomy
            5. Promotion of beneficial outcomes
            
            Current context: {context.summary if context.summary else 'New conversation'}
            """
            )

            # Process with enhanced prompt
            response = await chain.apredict(input=enhanced_prompt)

            # Calculate confidence score
            confidence = await self._calculate_response_confidence(response, message)

            # Create response object
            chat_response = ChatResponse(
                message_id=message.id,
                content=response,
                message_type=MessageType.TEXT,
                confidence=confidence,
                provider=provider,
                processing_time=(datetime.utcnow() - message.timestamp).total_seconds(),
                constitutional_hash=self.constitutional_hash,
            )

            # Store in conversation history
            await self._store_conversation_turn(
                context.conversation_id, message, chat_response
            )

            return chat_response

        except Exception as e:
            logger.error(f"Single model processing failed: {e}")
            raise

    async def _check_message_compliance(self, message: ChatMessage) -> Dict[str, Any]:
        """Check constitutional compliance of message."""
        try:
            # Constitutional principles
            principles = [
                "respects human dignity",
                "promotes beneficial outcomes",
                "avoids harmful content",
                "respects privacy",
                "promotes truthfulness",
            ]

            # Encode message
            with torch.no_grad():
                inputs = self.compliance_tokenizer(
                    message.content,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                )
                message_embedding = self.compliance_model(
                    **inputs
                ).last_hidden_state.mean(dim=1)

                # Check against harmful patterns
                harmful_patterns = [
                    "requests illegal activities",
                    "promotes violence or harm",
                    "contains hate speech",
                    "violates privacy",
                    "spreads misinformation",
                ]

                compliance_scores = {}
                for pattern in harmful_patterns:
                    pattern_inputs = self.compliance_tokenizer(
                        pattern, return_tensors="pt", truncation=True, max_length=512
                    )
                    pattern_embedding = self.compliance_model(
                        **pattern_inputs
                    ).last_hidden_state.mean(dim=1)

                    similarity = torch.cosine_similarity(
                        message_embedding, pattern_embedding
                    )
                    compliance_scores[pattern] = float(similarity)

                # Determine compliance
                max_violation = max(compliance_scores.values())
                compliant = max_violation < 0.6  # Threshold for violations

                return {
                    "compliant": compliant,
                    "scores": compliance_scores,
                    "max_violation": max_violation,
                    "reason": (
                        f"High similarity to harmful pattern"
                        if not compliant
                        else "Compliant"
                    ),
                }

        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {"compliant": True, "reason": "Compliance check failed"}

    async def _create_enhanced_prompt(
        self, message: ChatMessage, context: ConversationContext
    ) -> str:
        """Create enhanced prompt with constitutional context."""
        try:
            enhanced_prompt = f"""
            User Message: {message.content}
            
            Context Information:
            - Conversation ID: {context.conversation_id}
            - User ID: {context.user_id}
            - Constitutional Hash: {self.constitutional_hash}
            
            Please provide a helpful, accurate, and constitutionally compliant response.
            """

            # Add context-specific enhancements
            if context.domain:
                enhanced_prompt += f"\nDomain Context: {context.domain}"

            if context.constraints:
                enhanced_prompt += f"\nConstraints: {', '.join(context.constraints)}"

            return enhanced_prompt

        except Exception as e:
            logger.error(f"Prompt enhancement failed: {e}")
            return message.content

    async def _summarize_conversation(self, history: List[Dict[str, Any]]) -> str:
        """Summarize long conversation history."""
        try:
            # Combine recent messages for summarization
            recent_messages = history[-20:]  # Last 20 messages

            conversation_text = "\n".join(
                [
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in recent_messages
                ]
            )

            # Summarize using BART
            summary = self.summarizer(
                conversation_text, max_length=200, min_length=50, do_sample=False
            )

            return summary[0]["summary_text"]

        except Exception as e:
            logger.error(f"Conversation summarization failed: {e}")
            return "Previous conversation context unavailable"

    async def _calculate_response_confidence(
        self, response: str, message: ChatMessage
    ) -> float:
        """Calculate confidence score for response."""
        try:
            # Simple confidence heuristics
            confidence_factors = []

            # Length factor
            if 50 <= len(response) <= 500:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.6)

            # Coherence factor (simplified)
            sentences = response.split(".")
            if len(sentences) > 1:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.7)

            # Constitutional compliance factor
            if (
                self.constitutional_hash in response
                or "constitutional" in response.lower()
            ):
                confidence_factors.append(0.95)
            else:
                confidence_factors.append(0.8)

            return sum(confidence_factors) / len(confidence_factors)

        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5

    async def _enhance_response(
        self, response: ChatResponse, context: ConversationContext
    ) -> ChatResponse:
        """Enhance response with additional analysis."""
        try:
            # Add metadata
            response.metadata["enhanced"] = True
            response.metadata["analysis_timestamp"] = datetime.utcnow().isoformat()

            # Add conversation analytics
            if context.enable_analytics:
                analytics = await self._generate_conversation_analytics(
                    context.conversation_id
                )
                response.metadata["analytics"] = analytics

            return response

        except Exception as e:
            logger.error(f"Response enhancement failed: {e}")
            return response

    async def process_voice_message(
        self, audio_data: bytes, context: ConversationContext
    ) -> ChatResponse:
        """Process voice message with speech recognition."""
        try:
            # Convert audio to text
            text = await self._speech_to_text(audio_data)

            if not text:
                return ChatResponse(
                    message_id="voice_error",
                    content="Could not understand the audio message",
                    message_type=MessageType.ERROR,
                    confidence=0.0,
                    constitutional_hash=self.constitutional_hash,
                )

            # Create text message from transcription
            voice_message = ChatMessage(
                content=text,
                message_type=MessageType.VOICE,
                user_id=context.user_id,
                metadata={"transcribed_from_voice": True},
            )

            # Process as regular message
            response = await self.process_message_advanced(voice_message, context)

            # Generate audio response if requested
            if context.enable_voice_response:
                audio_response = await self._text_to_speech(response.content)
                response.metadata["audio_response"] = base64.b64encode(
                    audio_response
                ).decode()

            return response

        except Exception as e:
            logger.error(f"Voice message processing failed: {e}")
            raise

    async def _speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text."""
        try:
            # Create audio source from bytes
            audio_source = sr.AudioData(audio_data, 16000, 2)

            # Recognize speech
            text = self.speech_recognizer.recognize_google(audio_source)

            return text

        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return ""

    async def _text_to_speech(self, text: str) -> bytes:
        """Convert text to speech."""
        try:
            # Create audio buffer
            audio_buffer = io.BytesIO()

            # Generate speech
            self.tts_engine.save_to_file(text, audio_buffer)
            self.tts_engine.runAndWait()

            audio_buffer.seek(0)
            return audio_buffer.read()

        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            return b""

    async def _load_conversation_history(
        self, conversation_id: str
    ) -> List[Dict[str, Any]]:
        """Load conversation history from Redis."""
        try:
            if not self.redis_client:
                return []

            history_key = f"conversation:{conversation_id}"
            history_data = await self.redis_client.lrange(history_key, 0, -1)

            history = []
            for item in history_data:
                try:
                    history.append(json.loads(item))
                except json.JSONDecodeError:
                    continue

            return history

        except Exception as e:
            logger.error(f"Failed to load conversation history: {e}")
            return []

    async def _store_conversation_turn(
        self, conversation_id: str, message: ChatMessage, response: ChatResponse
    ):
        """Store conversation turn in Redis."""
        try:
            if not self.redis_client:
                return

            # Store user message
            user_turn = {
                "role": "user",
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "message_id": message.id,
            }

            # Store assistant response
            assistant_turn = {
                "role": "assistant",
                "content": response.content,
                "timestamp": datetime.utcnow().isoformat(),
                "message_id": response.message_id,
                "confidence": response.confidence,
                "provider": response.provider.value,
            }

            history_key = f"conversation:{conversation_id}"

            # Add to conversation history
            await self.redis_client.lpush(history_key, json.dumps(user_turn))
            await self.redis_client.lpush(history_key, json.dumps(assistant_turn))

            # Set expiration (7 days)
            await self.redis_client.expire(history_key, 604800)

        except Exception as e:
            logger.error(f"Failed to store conversation turn: {e}")

    async def _generate_conversation_analytics(
        self, conversation_id: str
    ) -> Dict[str, Any]:
        """Generate conversation analytics."""
        try:
            history = await self._load_conversation_history(conversation_id)

            if not history:
                return {}

            # Calculate metrics
            total_turns = len(history) // 2  # User + assistant pairs
            user_messages = [msg for msg in history if msg.get("role") == "user"]
            assistant_messages = [
                msg for msg in history if msg.get("role") == "assistant"
            ]

            analytics = {
                "total_turns": total_turns,
                "user_message_count": len(user_messages),
                "assistant_message_count": len(assistant_messages),
                "average_confidence": (
                    sum(msg.get("confidence", 0) for msg in assistant_messages)
                    / len(assistant_messages)
                    if assistant_messages
                    else 0
                ),
                "conversation_duration": (
                    (
                        datetime.fromisoformat(history[0]["timestamp"])
                        - datetime.fromisoformat(history[-1]["timestamp"])
                    ).total_seconds()
                    if len(history) > 1
                    else 0
                ),
            }

            return analytics

        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            return {}

    async def health_check(self) -> bool:
        """Check if all chat services are healthy."""
        try:
            # Test LLM providers
            for provider, llm in self.llm_providers.items():
                try:
                    test_response = await llm.ainvoke([HumanMessage(content="Hello")])
                    if not test_response.content:
                        return False
                except Exception as e:
                    logger.error(f"Health check failed for {provider}: {e}")
                    return False

            # Test Redis connection
            if self.redis_client:
                await self.redis_client.ping()

            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
