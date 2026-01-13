#!/usr/bin/env python3
"""Simplest Strands agent example."""

from strands import Agent

# Create an agent with default settings
agent = Agent()

# Ask the agent a question
response = agent("Tell me about agentic AI")
print(response)
