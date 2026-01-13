# CBA Indicator Selection Assistant

A chatbot for the Circular Bioeconomy Alliance (CBA) that helps users discover and select indicators from the CBA Knowledge Base. Built with [Strands Agents](https://github.com/strands-agents/strands-agents) and AWS Bedrock.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- AWS credentials with access to:
  - Amazon Bedrock (Claude model)
  - Amazon Bedrock Knowledge Base

## Setup

1. Clone the repository:
```bash
git clone https://github.com/CircularBioeconomyAlliance/coffee-recipe.git
cd coffee-recipe
```

2. Install dependencies:
```bash
uv sync
```

3. Configure AWS credentials:
```bash
export AWS_DEFAULT_REGION=us-west-2
# Ensure AWS credentials are configured (via ~/.aws/credentials, environment variables, or IAM role)
```

## Running the Application

### Streamlit Web UI

```bash
uv run streamlit run src/app.py
```

Opens a web interface at `http://localhost:8501` with:
- CBA-branded chat interface
- Session management
- File upload support

### CLI Agent

```bash
uv run src/agent.py
```

Interactive command-line chat. Type your messages and press Enter. Type `exit` to quit.

## Project Structure

```
coffee-recipe/
├── src/
│   ├── agent.py          # CLI chatbot agent
│   ├── app.py            # Streamlit web UI
│   └── prompts/
│       └── system.txt    # System prompt
├── tests/
│   ├── test_chat_app.py  # Integration tests
│   ├── test_cba_ui.py    # Branding tests
│   └── test_functions.py # Unit tests
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

## Running Tests

```bash
uv run python tests/test_functions.py
uv run python tests/test_cba_ui.py
uv run python tests/test_chat_app.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_DEFAULT_REGION` | AWS region for Bedrock | `us-west-2` |
| `STRANDS_KNOWLEDGE_BASE_ID` | Bedrock Knowledge Base ID | Set in code |
