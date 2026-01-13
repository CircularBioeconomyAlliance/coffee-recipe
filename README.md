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

   To run the application locally, you will need to set the following credentials in your terminal session:

   ```
   AWS_DEFAULT_REGION=us-west-2
   AWS_ACCESS_KEY_ID=<your-access-key>
   AWS_SECRET_ACCESS_KEY=<your-secret-key>
   AWS_SESSION_TOKEN=<your-session-token>
   ```

   AWS credentials can be obtained from [Workshop Studio](https://catalog.workshops.aws/).

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
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `AWS_SESSION_TOKEN` | AWS session token | Required |
| `STRANDS_KNOWLEDGE_BASE_ID` | Bedrock Knowledge Base ID | Set in code |
