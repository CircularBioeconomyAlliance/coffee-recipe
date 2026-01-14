#!/usr/bin/env python3
"""Bedrock AgentCore Runtime deployment wrapper for CBA agent with session management."""

import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Tuple

# Add the src directory to Python path for imports when running as script
_src_dir = Path(__file__).parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands_tools import current_time, file_write, http_request, memory, use_llm

# Import shared configuration
from config import (
    AGENTCORE_MEMORY_ID,
    AWS_REGION,
    KNOWLEDGE_BASE_ID,
    MODEL_ID,
    SYSTEM_PROMPT,
)

# Try to import AgentCore Memory integration, fall back to no session management if not available
MEMORY_INTEGRATION_AVAILABLE = False
try:
    from bedrock_agentcore.memory.integrations.strands.config import (
        AgentCoreMemoryConfig as _AgentCoreMemoryConfig,
    )
    from bedrock_agentcore.memory.integrations.strands.config import (
        RetrievalConfig as _RetrievalConfig,
    )
    from bedrock_agentcore.memory.integrations.strands.session_manager import (
        AgentCoreMemorySessionManager as _AgentCoreMemorySessionManager,
    )

    # Assign to module-level names after successful import
    AgentCoreMemoryConfig: Any = _AgentCoreMemoryConfig
    RetrievalConfig: Any = _RetrievalConfig
    AgentCoreMemorySessionManager: Any = _AgentCoreMemorySessionManager
    MEMORY_INTEGRATION_AVAILABLE = True
except (ImportError, AttributeError) as e:
    # Provide placeholder types for type checking
    AgentCoreMemoryConfig = None  # type: ignore[misc]
    RetrievalConfig = None  # type: ignore[misc]
    AgentCoreMemorySessionManager = None  # type: ignore[misc]
    print(f"⚠️  Warning: AgentCore Memory integration not available: {e}")
    print("   Using in-memory session management instead.")
    print("   Sessions will persist during agent lifetime but not across restarts.")

# Initialize the AgentCore app
app = BedrockAgentCoreApp()

# Verify KB is configured
print(f"Using Bedrock Knowledge Base ID: {KNOWLEDGE_BASE_ID}")

# Verify Memory is configured if integration is available
if MEMORY_INTEGRATION_AVAILABLE and AGENTCORE_MEMORY_ID:
    print(f"Using AgentCore Memory ID: {AGENTCORE_MEMORY_ID}")
elif MEMORY_INTEGRATION_AVAILABLE and not AGENTCORE_MEMORY_ID:
    print(
        "⚠️  Warning: AgentCore Memory integration available but AGENTCORE_MEMORY_ID not set."
    )
    print("   Run scripts/setup_memory.py to create memory resource.")
    print("   Sessions will work but without persistence across restarts.")

# Configure the Bedrock model (shared across all agents)
bedrock_model = BedrockModel(
    model_id=MODEL_ID,
    temperature=0.2,
)

# Agent cache with TTL - stores (agent, last_accessed_time)
agent_cache: Dict[str, Tuple[Agent, datetime]] = {}
AGENT_CACHE_MAX_SIZE = 100
AGENT_CACHE_TTL_HOURS = 1


def cleanup_expired_agents():
    """Remove expired agents from cache based on TTL."""
    now = datetime.now()
    expired_keys = [
        key
        for key, (_, last_accessed) in agent_cache.items()
        if now - last_accessed > timedelta(hours=AGENT_CACHE_TTL_HOURS)
    ]
    for key in expired_keys:
        del agent_cache[key]

    # If still over max size, remove oldest entries
    if len(agent_cache) > AGENT_CACHE_MAX_SIZE:
        sorted_items = sorted(agent_cache.items(), key=lambda x: x[1][1])
        for key, _ in sorted_items[: len(agent_cache) - AGENT_CACHE_MAX_SIZE]:
            del agent_cache[key]


def create_agent_with_session(session_id: str, actor_id: str) -> Agent:
    """
    Create or retrieve a cached agent with session management.

    Args:
        session_id: Unique session identifier
        actor_id: Unique user/actor identifier

    Returns:
        Agent configured with session management
    """
    cache_key = f"{actor_id}:{session_id}"

    # Check cache
    if cache_key in agent_cache:
        agent, _ = agent_cache[cache_key]
        # Update last accessed time
        agent_cache[cache_key] = (agent, datetime.now())
        return agent

    # Clean up expired agents before creating new one
    cleanup_expired_agents()

    # Create new agent with session management if available
    if MEMORY_INTEGRATION_AVAILABLE and AGENTCORE_MEMORY_ID:
        config = AgentCoreMemoryConfig(
            memory_id=AGENTCORE_MEMORY_ID,
            session_id=session_id,
            actor_id=actor_id,
            retrieval_config={
                # User preferences: budget, technical capacity, preferred indicators
                "/preferences/{actorId}": RetrievalConfig(top_k=5, relevance_score=0.7),
                # Project facts: location, crop type, expected outcomes
                "/facts/{actorId}": RetrievalConfig(top_k=10, relevance_score=0.5),
                # Session summaries: previous conversations
                "/summaries/{actorId}/{sessionId}": RetrievalConfig(
                    top_k=5, relevance_score=0.6
                ),
            },
        )

        session_manager = AgentCoreMemorySessionManager(
            agentcore_memory_config=config, region_name=AWS_REGION
        )

        agent = Agent(
            model=bedrock_model,
            system_prompt=SYSTEM_PROMPT,
            session_manager=session_manager,
            tools=[
                memory,
                use_llm,
                http_request,
                file_write,
                current_time,
            ],
        )
    else:
        # Fall back to agent without session management
        agent = Agent(
            model=bedrock_model,
            system_prompt=SYSTEM_PROMPT,
            tools=[
                memory,
                use_llm,
                http_request,
                file_write,
                current_time,
            ],
        )

    # Cache the agent
    agent_cache[cache_key] = (agent, datetime.now())

    return agent


@app.entrypoint
def invoke(payload):
    """
    Process user input and return a response with session management.

    Expected payload format:
    {
        "prompt": "User message here",
        "session_id": "optional-session-uuid",
        "actor_id": "optional-user-identifier",
        "file_content": "Optional file content for context"
    }

    Returns:
    {
        "result": "Agent response",
        "status": "success",
        "session_id": "session-uuid",
        "actor_id": "user-identifier"
    }
    """
    user_message = payload.get("prompt", "")
    file_content = payload.get("file_content", None)

    # Get or generate session identifiers
    session_id = payload.get("session_id", str(uuid.uuid4()))
    actor_id = payload.get("actor_id", "default-user")

    if not user_message:
        return {
            "error": "No prompt found in input. Please provide a 'prompt' key in the payload.",
            "status": "error",
            "session_id": session_id,
            "actor_id": actor_id,
        }

    # Get or create agent with session management
    session_agent = create_agent_with_session(session_id, actor_id)

    # Build the prompt with file context if available
    if file_content and file_content.strip():
        full_prompt = f"""User question: {user_message}

The user has also provided the following document content for context:
---
{file_content[:2000]}{'...[truncated]' if len(file_content) > 2000 else ''}
---

Please consider this document when answering."""
    else:
        full_prompt = user_message

    # Get response from agent (conversation history is maintained automatically)
    result = session_agent(full_prompt)

    # Return structured response with session info
    return {
        "result": str(result),
        "status": "success",
        "session_id": session_id,
        "actor_id": actor_id,
        "cache_size": len(agent_cache),
    }


if __name__ == "__main__":
    app.run()
