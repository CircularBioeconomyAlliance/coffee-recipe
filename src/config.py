"""Shared configuration for the CBA application."""

import os
from pathlib import Path

# AWS Bedrock configuration
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
KNOWLEDGE_BASE_ID = "0ZQBMXEKDI"
AWS_REGION = "us-west-2"

# Set environment variables
os.environ["AWS_DEFAULT_REGION"] = AWS_REGION
os.environ["STRANDS_KNOWLEDGE_BASE_ID"] = KNOWLEDGE_BASE_ID

# Load system prompt from text file
PROMPTS_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "system.txt").read_text()
