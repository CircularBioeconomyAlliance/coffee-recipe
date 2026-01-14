#!/usr/bin/env python3
"""
Invoke the deployed CBA Indicator Assistant agent on Bedrock AgentCore Runtime.

This script demonstrates:
- Multi-turn conversations with session persistence
- AgentCore Memory integration (STM + LTM)
- How the agent remembers context across requests

Desired Outcomes:
- Agent retrieves relevant indicators from Knowledge Base
- Agent remembers user preferences (budget, technical capacity)
- Agent provides contextual recommendations based on project details
- Session continuity enables natural multi-turn conversations
"""

import json
import sys
import uuid
from pathlib import Path

import boto3
import yaml


def load_agent_config():
    """Load agent configuration from .bedrock_agentcore.yaml"""
    config_path = Path(".bedrock_agentcore.yaml")

    if not config_path.exists():
        print("❌ Error: .bedrock_agentcore.yaml not found")
        print("Please run 'uv run agentcore configure' first")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    default_agent = config.get("default_agent")
    if not default_agent:
        print("❌ Error: No default agent configured")
        sys.exit(1)

    agent_config = config["agents"].get(default_agent)
    if not agent_config:
        print(f"❌ Error: Agent '{default_agent}' not found in config")
        sys.exit(1)

    agent_arn = agent_config.get("bedrock_agentcore", {}).get("agent_arn")
    region = agent_config.get("aws", {}).get("region", "us-west-2")

    if not agent_arn:
        print("❌ Error: Agent ARN not found in config")
        print("Please deploy your agent with 'uv run agentcore launch' first")
        sys.exit(1)

    return agent_arn, region


def invoke_agent(
    agent_arn,
    prompt,
    runtime_session_id=None,
    session_id=None,
    actor_id=None,
    file_content=None,
    region="us-west-2",
):
    """
    Invoke the deployed agent with a prompt and session management.

    Args:
        agent_arn: ARN of the deployed agent runtime
        prompt: User message/prompt
        runtime_session_id: AgentCore Runtime session ID for microVM isolation
                           (reuse for multi-turn conversations)
        session_id: Agent memory session ID for conversation continuity
        actor_id: User identifier for cross-session memory (defaults to "default-user")
        file_content: Optional file content for context
        region: AWS region (default: us-west-2)

    Returns:
        Tuple of (response_data, runtime_session_id, session_id, actor_id)
    """
    try:
        client = boto3.client("bedrock-agentcore", region_name=region)

        # Generate runtime_session_id if not provided (must be 33+ characters)
        # IMPORTANT: Reuse the same runtime_session_id for multi-turn conversations
        if runtime_session_id is None:
            runtime_session_id = str(uuid.uuid4()) + "-session"

        # Generate session_id and actor_id if not provided (for agent memory)
        if session_id is None:
            session_id = str(uuid.uuid4())
        if actor_id is None:
            actor_id = "default-user"

        # Prepare the payload with session management
        payload_data = {
            "prompt": prompt,
            "session_id": session_id,
            "actor_id": actor_id,
        }
        if file_content:
            payload_data["file_content"] = file_content

        payload = json.dumps(payload_data).encode()

        print(f"Prompt: {prompt}")

        # Invoke the agent
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=runtime_session_id,
            payload=payload,
            qualifier="DEFAULT",
        )

        # Read and parse the response
        response_body = response["response"].read()
        response_data = json.loads(response_body)

        result = response_data.get("result", "No result")
        print(f"\nAgent Response:\n{result}\n")

        return response_data, runtime_session_id, session_id, actor_id

    except Exception as e:
        print(f"\n❌ Error invoking agent: {str(e)}")
        sys.exit(1)


def run_multi_turn_conversation(agent_arn, region):
    """
    Demonstrate multi-turn conversation with session management.

    This shows how the agent maintains context across multiple requests
    using the same runtime_session_id, session_id, and actor_id.

    Session Management Architecture:
    - runtime_session_id: AgentCore Runtime microVM isolation (keeps environment alive)
    - session_id: Agent's AgentCore Memory session (conversation history)
    - actor_id: User identifier for cross-session long-term memory

    Desired Outcomes:
    - Turn 1: Agent asks clarifying questions about project type/location
    - Turn 2: Agent acknowledges cotton project in Chad, asks about constraints
    - Turn 3: Agent notes budget/capacity constraints, may start searching KB
    - Turn 4: Agent provides specific indicator recommendations from KB,
              tailored to the cotton/Chad/low-budget context
    """
    print("\n" + "=" * 70)
    print("MULTI-TURN CONVERSATION DEMO")
    print("=" * 70)
    print("\nThis demonstrates session management with AgentCore Memory.")
    print("The agent will remember context across multiple requests.")
    print("\n📋 DESIRED OUTCOMES:")
    print("   • Agent should ask clarifying questions initially")
    print("   • Agent should remember project details across turns")
    print("   • Agent should search Knowledge Base for relevant indicators")
    print("   • Final response should include specific indicator recommendations")
    print(
        "   • Recommendations should match constraints (low budget, basic capacity)\n"
    )

    # Generate session identifiers for this conversation
    # All three IDs are reused across all turns to maintain context
    runtime_session_id = str(uuid.uuid4()) + "-runtime"  # AgentCore Runtime session
    session_id = str(uuid.uuid4())  # Agent memory session
    actor_id = f"demo-user-{uuid.uuid4().hex[:8]}"  # User identifier

    print(f"Runtime Session ID: {runtime_session_id}")
    print(f"Memory Session ID:  {session_id}")
    print(f"Actor ID:           {actor_id}\n")
    print("=" * 70)

    # Multi-turn conversation flow
    conversation = [
        "I need help selecting indicators for a project.",
        "It's a cotton farming project in Chad.",
        "We have a low budget and basic technical capacity, but want to improve the soil quality and stop erosion.",
        "What indicators would you recommend?",
    ]

    for i, prompt in enumerate(conversation, 1):
        print(f"\n[Turn {i}]")
        print("-" * 70)
        response, runtime_session_id, session_id, actor_id = invoke_agent(
            agent_arn,
            prompt,
            runtime_session_id=runtime_session_id,  # Reuse runtime session
            session_id=session_id,  # Reuse memory session
            actor_id=actor_id,  # Reuse actor ID
            region=region,
        )
        print("-" * 70)

    print("\n" + "=" * 70)
    print("CONVERSATION COMPLETE")
    print("=" * 70)
    print("\n📊 SESSION SUMMARY:")
    print(f"  Runtime Session: {runtime_session_id}")
    print(f"  Memory Session:  {session_id}")
    print(f"  Actor ID:        {actor_id}")
    print("\n✅ VALIDATION CHECKLIST:")
    print("   Did the agent...")
    print("   [ ] Remember the project type (cotton farming)?")
    print("   [ ] Remember the location (Chad)?")
    print("   [ ] Remember the constraints (low budget, basic capacity)?")
    print("   [ ] Search the Knowledge Base for indicators?")
    print("   [ ] Provide specific indicator IDs and methods?")
    print("   [ ] Tailor recommendations to the stated constraints?")
    print("\n🔧 MEMORY ARCHITECTURE POWERING THIS:")
    print("   • STM: Conversation history within this session")
    print("   • LTM Summaries: Will be generated at session end")
    print("   • LTM Preferences: Budget/capacity preferences stored for future")
    print("   • LTM Facts: Project location/type stored for future sessions")
    print("\n💡 TIP: Run this demo again with the same actor_id to see")
    print("   how LTM remembers your preferences across sessions!")
    print("=" * 70)


def run_interactive_session(agent_arn, region):
    """
    Run an interactive chat session with the agent.
    Type 'quit' or 'exit' to end the session.

    Desired Outcomes:
    - Natural multi-turn conversation flow
    - Agent remembers context from earlier in the conversation
    - Agent searches Knowledge Base when asked about indicators
    - Responses are tailored to user's stated preferences
    """
    print("\n" + "=" * 70)
    print("INTERACTIVE CHAT SESSION")
    print("=" * 70)
    print("\nYou can have a multi-turn conversation with the agent.")
    print("The agent will remember everything you say in this session.")
    print("\n📋 SUGGESTED CONVERSATION FLOW:")
    print("   1. Start with: 'I need help selecting indicators'")
    print("   2. Describe your project type and location")
    print("   3. Mention your budget and technical capacity")
    print("   4. Ask for specific indicator recommendations")
    print("\nType 'quit' or 'exit' to end the session.\n")

    # Generate session identifiers
    runtime_session_id = str(uuid.uuid4()) + "-interactive"
    session_id = str(uuid.uuid4())
    actor_id = f"interactive-user-{uuid.uuid4().hex[:8]}"

    print(f"Session started with:")
    print(f"  Runtime Session: {runtime_session_id[:20]}...")
    print(f"  Memory Session:  {session_id[:20]}...")
    print(f"  Actor ID:        {actor_id}")
    print("=" * 70)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye!")
                break

            print()
            response, runtime_session_id, session_id, actor_id = invoke_agent(
                agent_arn,
                user_input,
                runtime_session_id=runtime_session_id,
                session_id=session_id,
                actor_id=actor_id,
                region=region,
            )

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break


if __name__ == "__main__":
    # Load configuration from .bedrock_agentcore.yaml
    AGENT_ARN, REGION = load_agent_config()

    print("=" * 70)
    print("CBA INDICATOR ASSISTANT - Agent Invocation Test")
    print("=" * 70)
    print(f"\n✓ Agent ARN: {AGENT_ARN}")
    print(f"✓ Region: {REGION}")
    print("\n📎 This agent helps select CBA indicators from a Knowledge Base.")
    print("   It uses AgentCore Memory for session continuity and learning.\n")

    # Prompt user for demo choice
    print("Choose a test mode:")
    print("1. Multi-turn conversation demo (scripted) - See memory in action")
    print("2. Interactive chat session - Free-form conversation")
    print("3. Single prompt test - Quick one-shot query")
    print("\nEnter choice (1, 2, or 3, default: 1):")
    choice = input("> ").strip()

    if choice == "2":
        # Interactive session
        run_interactive_session(AGENT_ARN, REGION)

    elif choice == "3":
        # Single prompt mode
        EXAMPLE_PROMPTS = [
            "What indicators should I use for a cotton farming project in Chad with low budget?",
            "Recommend soil health indicators for smallholder farmers in sub-Saharan Africa",
            "What are the best methods to measure carbon sequestration in agroforestry systems?",
        ]

        print("\n📋 DESIRED OUTCOME:")
        print("   Agent should search the Knowledge Base and return specific")
        print("   indicator recommendations with IDs, methods, and rationale.\n")
        print("Example prompts:")
        for i, prompt in enumerate(EXAMPLE_PROMPTS, 1):
            print(f"{i}. {prompt}")

        print("\nEnter your prompt (or press Enter to use example 1):")
        user_prompt = input("> ").strip()

        if not user_prompt:
            user_prompt = EXAMPLE_PROMPTS[0]

        print("\n" + "=" * 70)
        response, _, session_id, actor_id = invoke_agent(
            AGENT_ARN, user_prompt, region=REGION
        )
        print("=" * 70)
        print("\nFull Response:")
        print(json.dumps(response, indent=2))
    else:
        # Multi-turn conversation demo (default)
        run_multi_turn_conversation(AGENT_ARN, REGION)
