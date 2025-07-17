"""
Conversation Manager - Handles conversation state and persistence
Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import redis
from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime, timedelta
import logging
import asyncio

from ..models.schemas import (
    ConversationMessage, 
    ConversationHistory, 
    ConversationContext, 
    ConversationStatus,
    MessageRole,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Manages conversation state, history, and persistence with Redis backend.
    Provides context-aware conversation handling with constitutional compliance.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize conversation manager with Redis connection."""
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.conversation_ttl = 86400 * 7  # 7 days
        self.max_context_messages = 20  # Maximum messages to keep in context
        
    async def create_conversation(self, context: ConversationContext) -> ConversationHistory:
        """Create a new conversation with context."""
        try:
            conversation_id = context.conversation_id
            
            # Create conversation history
            conversation = ConversationHistory(
                conversation_id=conversation_id,
                messages=[],
                status=ConversationStatus.ACTIVE,
                context=context,
                constitutional_hash=self.constitutional_hash
            )
            
            # Store in Redis
            await self._store_conversation(conversation)
            
            logger.info(f"Created new conversation: {conversation_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationHistory]:
        """Retrieve conversation by ID."""
        try:
            conversation_key = f"conversation:{conversation_id}"
            conversation_data = self.redis_client.get(conversation_key)
            
            if not conversation_data:
                return None
            
            # Deserialize conversation
            data = json.loads(conversation_data)
            conversation = ConversationHistory(**data)
            
            # Validate constitutional hash
            if conversation.constitutional_hash != self.constitutional_hash:
                logger.warning(f"Constitutional hash mismatch for conversation {conversation_id}")
                return None
            
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation {conversation_id}: {e}")
            return None
    
    async def add_message(self, conversation_id: str, message: ConversationMessage) -> bool:
        """Add a message to the conversation."""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                logger.error(f"Conversation {conversation_id} not found")
                return False
            
            # Add message to history
            conversation.messages.append(message)
            conversation.updated_at = datetime.utcnow()
            
            # Trim context if too long
            if len(conversation.messages) > self.max_context_messages:
                # Keep system messages and recent messages
                system_messages = [msg for msg in conversation.messages if msg.role == MessageRole.SYSTEM]
                recent_messages = conversation.messages[-(self.max_context_messages - len(system_messages)):]
                conversation.messages = system_messages + recent_messages
            
            # Store updated conversation
            await self._store_conversation(conversation)
            
            logger.info(f"Added message to conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
            return False
    
    async def get_conversation_context(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation context in format suitable for LLM."""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return []
            
            # Convert messages to LLM format
            context = []
            for message in conversation.messages:
                context.append({
                    "role": message.role.value,
                    "content": message.content
                })
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get context for conversation {conversation_id}: {e}")
            return []
    
    async def update_conversation_status(self, conversation_id: str, status: ConversationStatus) -> bool:
        """Update conversation status."""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return False
            
            conversation.status = status
            conversation.updated_at = datetime.utcnow()
            
            await self._store_conversation(conversation)
            
            logger.info(f"Updated conversation {conversation_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update conversation status: {e}")
            return False
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        try:
            conversation_key = f"conversation:{conversation_id}"
            result = self.redis_client.delete(conversation_key)
            
            if result:
                logger.info(f"Deleted conversation {conversation_id}")
                return True
            else:
                logger.warning(f"Conversation {conversation_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False
    
    async def search_conversations(self, user_id: str, query: str = "", limit: int = 10) -> List[ConversationHistory]:
        """Search conversations for a user."""
        try:
            # Get all conversation keys for user
            pattern = f"conversation:*"
            keys = self.redis_client.keys(pattern)
            
            conversations = []
            for key in keys:
                conversation_data = self.redis_client.get(key)
                if conversation_data:
                    data = json.loads(conversation_data)
                    conversation = ConversationHistory(**data)
                    
                    # Filter by user
                    if conversation.context and conversation.context.user_id == user_id:
                        # Simple text search in messages
                        if not query or self._matches_query(conversation, query):
                            conversations.append(conversation)
            
            # Sort by updated time and limit
            conversations.sort(key=lambda x: x.updated_at, reverse=True)
            return conversations[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return []
    
    async def get_conversation_analytics(self, user_id: str) -> Dict[str, any]:
        """Get analytics for user conversations."""
        try:
            conversations = await self.search_conversations(user_id)
            
            total_conversations = len(conversations)
            total_messages = sum(len(conv.messages) for conv in conversations)
            
            # Calculate average response time (mock for now)
            avg_response_time = 1.2  # seconds
            
            # Calculate compliance rate (mock for now)
            compliance_rate = 0.95
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "avg_response_time": avg_response_time,
                "compliance_rate": compliance_rate,
                "constitutional_hash": self.constitutional_hash
            }
            
        except Exception as e:
            logger.error(f"Failed to get conversation analytics: {e}")
            return {}
    
    async def _store_conversation(self, conversation: ConversationHistory):
        """Store conversation in Redis."""
        try:
            conversation_key = f"conversation:{conversation.conversation_id}"
            conversation_data = conversation.json()
            
            # Store with TTL
            self.redis_client.setex(
                conversation_key,
                self.conversation_ttl,
                conversation_data
            )
            
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            raise
    
    def _matches_query(self, conversation: ConversationHistory, query: str) -> bool:
        """Check if conversation matches search query."""
        query_lower = query.lower()
        
        # Search in message content
        for message in conversation.messages:
            if query_lower in message.content.lower():
                return True
        
        return False
    
    async def cleanup_expired_conversations(self):
        """Clean up expired conversations (background task)."""
        try:
            # Redis TTL handles expiration automatically
            # This method can be used for additional cleanup logic
            logger.info("Conversation cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup conversations: {e}")
    
    async def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """Generate a summary of the conversation."""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation or len(conversation.messages) == 0:
                return None
            
            # Simple summary - first and last messages
            first_msg = conversation.messages[0]
            last_msg = conversation.messages[-1]
            
            summary = f"Conversation started with: '{first_msg.content[:100]}...' "
            summary += f"and ended with: '{last_msg.content[:100]}...'"
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate conversation summary: {e}")
            return None