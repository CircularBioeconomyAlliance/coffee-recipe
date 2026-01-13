#!/usr/bin/env python3
"""Simple Strands chatbot with Bedrock knowledge base support."""

import os
from pathlib import Path

from strands import Agent
from strands_tools import current_time, file_write, http_request, memory, use_llm

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
KNOWLEDGE_BASE_ID = "CXRV29T1AF"

# Set AWS region and knowledge base ID
os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
os.environ["STRANDS_KNOWLEDGE_BASE_ID"] = KNOWLEDGE_BASE_ID

# Load system prompt from text file
PROMPTS_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "system.txt").read_text()


def main():
    print(f"Using Knowledge Base ID: {KNOWLEDGE_BASE_ID}")

    agent = Agent(
        model=MODEL_ID,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            memory,
            use_llm,
            http_request,
            file_write,
            current_time,
        ],
    )

    print("\nCBA Knowledge Base Chatbot")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("> ")

        if user_input.lower() in ["exit", "quit"]:
            print("\nGoodbye!")
            break

        if not user_input.strip():
            continue

        agent(user_input)
        print()


if __name__ == "__main__":
    main()
