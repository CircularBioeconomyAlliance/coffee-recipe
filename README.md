# CBA Indicator Selection Assistant

A structured workflow application for the Circular Bioeconomy Alliance (CBA) that guides users through indicator selection from the CBA Knowledge Base. Built with [Strands Agents](https://github.com/strands-agents/strands-agents) and AWS Bedrock.

## Workflow Overview

The application follows a deterministic, state-driven workflow to ensure comprehensive indicator selection:

1. **Upload** - Upload project documents (PDF, Excel, CSV, TXT) or skip to manual entry
2. **Extract** - Automatically extract project information from uploaded documents
3. **Ask** - Fill in any missing required project information
4. **Retrieve** - Get relevant indicators from the Knowledge Base based on your project
5. **Chat** - Ask questions about the recommended indicators and export results

This structured approach ensures all necessary project context is gathered before making indicator recommendations.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- AWS credentials with access to:
  - Amazon Bedrock (Claude model)
  - Amazon Bedrock Knowledge Base
  - Amazon S3 (for document uploads)

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

4. Configure S3 bucket for document uploads:

   The application uses an S3 bucket to store uploaded project documents. The default bucket name is `cba-project-docs`. 
   
   - Ensure the bucket exists in your AWS account (region: `us-west-2`)
   - Your AWS credentials must have permissions to upload objects to this bucket
   - Documents are organized with date-based prefixes: `uploads/YYYYMMDD/filename`

## Running the Application

### Streamlit Web UI (Recommended)

```bash
uv run streamlit run src/app.py
```

Opens a web interface at `http://localhost:8501` with:
- Structured workflow guidance through indicator selection
- CBA-branded chat interface
- Session management with persistent chat history
- File upload support for project documents
- Progress tracking through workflow phases

The web UI guides you through the complete workflow from document upload to indicator export.

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
│   ├── app.py            # Streamlit web UI with workflow
│   ├── config.py         # Shared configuration
│   ├── workflow.py       # Workflow helper functions
│   └── prompts/
│       └── system.txt    # System prompt
├── tests/
│   ├── test_chat_app.py      # Integration tests
│   ├── test_cba_ui.py        # Branding tests
│   ├── test_functions.py     # Unit tests
│   ├── test_workflow_e2e.py  # Workflow end-to-end tests
│   └── test_error_handling.py # Error handling tests
├── cba_inputs/           # Reference documents
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

## Running Tests

```bash
# Unit tests
uv run python tests/test_functions.py

# UI branding tests
uv run python tests/test_cba_ui.py

# Integration tests
uv run python tests/test_chat_app.py

# Workflow end-to-end tests
uv run python tests/test_workflow_e2e.py

# Error handling tests
uv run python tests/test_error_handling.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_DEFAULT_REGION` | AWS region for Bedrock | `us-west-2` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `AWS_SESSION_TOKEN` | AWS session token | Required |
| `STRANDS_KNOWLEDGE_BASE_ID` | Bedrock Knowledge Base ID | Set in code |

## Workflow Details

### Required Project Information

The workflow collects the following information to make accurate indicator recommendations:

- **Location** - Geographic location of the project
- **Project Type** - Type of circular bioeconomy initiative (e.g., "regenerative cotton farming")
- **Outcomes** - Desired project outcomes (e.g., "soil health", "water conservation")
- **Budget** - Available budget level (low, medium, high)
- **Capacity** - Technical capacity for measurement (basic, intermediate, advanced)

### Document Upload

Supported file formats:
- **PDF** - Text extraction from project documents
- **Excel** (.xlsx) - Data extraction from spreadsheets
- **CSV** - Comma-separated value files
- **TXT** - Plain text files

Documents are uploaded to S3 bucket `cba-project-docs` with automatic date-based organization.

### Knowledge Base Integration

The application uses AWS Bedrock Knowledge Base for indicator retrieval:
- Direct boto3 SDK calls for deterministic queries
- Structured queries built from project information
- No fabrication of indicators beyond Knowledge Base content
- Follow-up questions answered using additional KB queries

## Development

### Branch Strategy

Development work is done on feature branches:
- Main branch remains stable
- Feature branches for new functionality (e.g., `feature/workflow-refactor`)
- Merge to main only after thorough testing

### Architecture

The application uses a simple, functional architecture:
- **Session state** for workflow tracking
- **Helper functions** in `workflow.py` (no classes)
- **Direct boto3** for Knowledge Base access
- **Minimal changes** to existing codebase
