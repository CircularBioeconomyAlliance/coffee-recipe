#!/usr/bin/env python3
"""Invoke the deployed CBA agent on Bedrock AgentCore Runtime."""

import boto3
import json
import sys
import uuid
import yaml
from pathlib import Path

def load_agent_config():
    """Load agent configuration from .bedrock_agentcore.yaml"""
    config_path = Path(".bedrock_agentcore.yaml")
    
    if not config_path.exists():
        print("❌ Error: .bedrock_agentcore.yaml not found")
        print("Please run 'uv run agentcore configure' first")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    default_agent = config.get('default_agent')
    if not default_agent:
        print("❌ Error: No default agent configured")
        sys.exit(1)
    
    agent_config = config['agents'].get(default_agent)
    if not agent_config:
        print(f"❌ Error: Agent '{default_agent}' not found in config")
        sys.exit(1)
    
    agent_arn = agent_config.get('bedrock_agentcore', {}).get('agent_arn')
    region = agent_config.get('aws', {}).get('region', 'us-west-2')
    
    if not agent_arn:
        print("❌ Error: Agent ARN not found in config")
        print("Please deploy your agent with 'uv run agentcore launch' first")
        sys.exit(1)
    
    return agent_arn, region

def invoke_agent(agent_arn, prompt, file_content=None, region="us-west-2"):
    """
    Invoke the deployed agent with a prompt.
    
    Args:
        agent_arn: ARN of the deployed agent runtime
        prompt: User message/prompt
        file_content: Optional file content for context
        region: AWS region (default: us-west-2)
    """
    try:
        client = boto3.client('bedrock-agentcore', region_name=region)
        
        # Generate a session ID (must be 33+ characters)
        session_id = str(uuid.uuid4()) + "-session"
        
        # Prepare the payload
        payload_data = {"prompt": prompt}
        if file_content:
            payload_data["file_content"] = file_content
        
        payload = json.dumps(payload_data).encode()
        
        print(f"Invoking agent: {agent_arn}")
        print(f"Session ID: {session_id}")
        print(f"Prompt: {prompt}\n")
        
        # Invoke the agent
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=payload,
            qualifier="DEFAULT"
        )
        
        # Read and parse the response
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        print("=" * 60)
        print("Agent Response:")
        print("=" * 60)
        print(json.dumps(response_data, indent=2))
        
        return response_data
        
    except Exception as e:
        print(f"\n❌ Error invoking agent: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Load configuration from .bedrock_agentcore.yaml
    AGENT_ARN, REGION = load_agent_config()
    
    # Example prompts
    EXAMPLE_PROMPTS = [
        "What are the key principles of circular bioeconomy?",
        "How can regenerative agriculture contribute to sustainability?",
        "What indicators should I use for a cotton farming project in Chad?"
    ]
    
    print("=" * 60)
    print("CBA Agent Invocation Test")
    print("=" * 60)
    print(f"\n✓ Loaded agent ARN: {AGENT_ARN}")
    print(f"✓ Region: {REGION}")
    print("\nExample prompts:")
    for i, prompt in enumerate(EXAMPLE_PROMPTS, 1):
        print(f"{i}. {prompt}")
    
    print("\nEnter your prompt (or press Enter to use example 1):")
    user_prompt = input("> ").strip()
    
    if not user_prompt:
        user_prompt = EXAMPLE_PROMPTS[0]
    
    invoke_agent(AGENT_ARN, user_prompt, region=REGION)
