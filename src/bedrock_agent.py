#!/usr/bin/env python3
"""Bedrock AgentCore Runtime deployment wrapper for CBA agent."""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands_tools import memory, use_llm, http_request, file_write, current_time

# Import shared configuration
from config import MODEL_ID, SYSTEM_PROMPT

# Initialize the AgentCore app
app = BedrockAgentCoreApp()

# Configure the Strands agent
bedrock_model = BedrockModel(
    model_id=MODEL_ID,
    temperature=0.2,
)

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


@app.entrypoint
def invoke(payload):
    """
    Process user input and return a response.
    
    Expected payload format:
    {
        "prompt": "User message here",
        "file_content": "Optional file content for context"
    }
    """
    user_message = payload.get("prompt", "")
    file_content = payload.get("file_content", None)
    
    if not user_message:
        return {
            "error": "No prompt found in input. Please provide a 'prompt' key in the payload.",
            "status": "error"
        }
    
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
    
    # Get response from agent
    result = agent(full_prompt)
    
    # Return structured response
    return {
        "result": str(result),
        "status": "success"
    }


if __name__ == "__main__":
    app.run()
