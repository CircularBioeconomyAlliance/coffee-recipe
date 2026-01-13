#!/usr/bin/env python3
"""Simple Strands chatbot with Bedrock knowledge base support."""

import os
from strands import Agent
from strands_tools import memory
from prompts import SYSTEM_PROMPT

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

# Set AWS region and knowledge base ID
os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
os.environ["STRANDS_KNOWLEDGE_BASE_ID"] = "CXRV29T1AF"


def main():
    agent = Agent(
        model=MODEL_ID,
        system_prompt=SYSTEM_PROMPT,
        tools=[memory],
    )

    print("\nKnowledge Base Chatbot")
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
