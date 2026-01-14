#!/usr/bin/env python3
"""
One-time setup script to create AgentCore Memory resource with Long-Term Memory strategies.

This script creates a Bedrock AgentCore Memory resource configured with three strategies:
- summaryMemoryStrategy: Summarize conversation sessions
- userPreferenceMemoryStrategy: Learn user preferences (budget, capacity, location)
- semanticMemoryStrategy: Store project facts across sessions

Usage:
    uv run scripts/setup_memory.py

The script will output the memory ID which should be added to your environment:
    export AGENTCORE_MEMORY_ID=<memory-id>
"""

import os
import sys

from bedrock_agentcore.memory import MemoryClient


def create_memory_resource(region_name="us-west-2"):
    """
    Create AgentCore Memory resource with LTM strategies.

    Args:
        region_name: AWS region for the memory resource (default: us-west-2)

    Returns:
        dict: Created memory resource information
    """
    print("=" * 70)
    print("CBA AgentCore Memory Setup")
    print("=" * 70)
    print(f"\nCreating memory resource in region: {region_name}\n")

    try:
        client = MemoryClient(region_name=region_name)

        print("Configuring memory with Long-Term Memory (LTM) strategies:")
        print("  1. summaryMemoryStrategy - Session summaries")
        print("  2. userPreferenceMemoryStrategy - User preferences")
        print("  3. semanticMemoryStrategy - Project facts")
        print("\nThis may take a few minutes...\n")

        memory = client.create_memory_and_wait(
            name="CBA_Indicator_Assistant_Memory",
            description="Memory resource for CBA Indicator Selection Assistant with conversation persistence, user preferences, and project facts storage",
            strategies=[
                {
                    "summaryMemoryStrategy": {
                        "name": "SessionSummarizer",
                        "namespaces": ["/summaries/{actorId}/{sessionId}"],
                    }
                },
                {
                    "userPreferenceMemoryStrategy": {
                        "name": "PreferenceLearner",
                        "namespaces": ["/preferences/{actorId}"],
                    }
                },
                {
                    "semanticMemoryStrategy": {
                        "name": "FactExtractor",
                        "namespaces": ["/facts/{actorId}"],
                    }
                },
            ],
        )

        memory_id = memory.get("id")

        print("✅ Memory resource created successfully!\n")
        print("=" * 70)
        print("Memory Details:")
        print("=" * 70)
        print(f"Memory ID: {memory_id}")
        print(f"Name: {memory.get('name')}")
        print(f"Status: {memory.get('status')}")
        print(f"Region: {region_name}")
        print("=" * 70)
        print("\n📝 Next Steps:")
        print("=" * 70)
        print("\n1. Add the following to your environment variables:")
        print(f"   export AGENTCORE_MEMORY_ID={memory_id}")
        print("\n2. Or add to src/config.py:")
        print(f'   AGENTCORE_MEMORY_ID = "{memory_id}"')
        print("\n3. Deploy your agent with the updated configuration")
        print("\n⚠️  Note: LTM strategies incur additional charges.")
        print("   Monitor usage in AWS Console > Bedrock > AgentCore Memory")
        print("=" * 70)

        return memory

    except Exception as e:
        print(f"\n❌ Error creating memory resource: {str(e)}")
        print("\nPlease ensure:")
        print("  - AWS credentials are configured")
        print("  - You have permissions for bedrock-agentcore:CreateMemory")
        print("  - The region supports Bedrock AgentCore Memory")
        sys.exit(1)


if __name__ == "__main__":
    # Allow region override via environment variable or command line
    region = os.environ.get("AWS_DEFAULT_REGION", "us-west-2")

    if len(sys.argv) > 1:
        region = sys.argv[1]

    print(f"Using region: {region}")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()

    create_memory_resource(region_name=region)
