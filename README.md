# CBA Indicator Selection Assistant

A chatbot for the Circular Bioeconomy Alliance (CBA) that helps users discover and select indicators from the CBA Knowledge Base. Built with [Strands Agents](https://github.com/strands-agents/strands-agents) and AWS Bedrock.

## Quick Start (Hackathon)

**Run the frontend locally with the pre-deployed AWS backend:**

```bash
git clone https://github.com/CircularBioeconomyAlliance/coffee-recipe.git
cd coffee-recipe/cba-frontend
npm install
npm run dev
```

Open http://localhost:3000 - the backend is already deployed on AWS!

See [DEPLOYMENT.md](DEPLOYMENT.md#hackathon-quick-start) for details.

## Documentation

| Document | Description |
|----------|-------------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment guide (start with Hackathon Quick Start) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture and data flow diagrams |
| [CODE_REVIEW.md](CODE_REVIEW.md) | Code review notes and known issues |
| [PRESENTER_GUIDE.md](PRESENTER_GUIDE.md) | Talking points for demos |

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
├── src/                          # Streamlit app & CLI agent
│   ├── agent.py                  # CLI chatbot agent
│   ├── app.py                    # Streamlit web UI
│   ├── config.py                 # Shared configuration
│   └── prompts/
│       └── system.txt            # System prompt
├── cba-frontend/                 # Next.js production frontend
│   ├── app/                      # App router pages
│   │   ├── chat/                 # Chat interface
│   │   ├── upload/               # File upload
│   │   ├── results/              # Indicator results
│   │   └── compare/              # Comparison view
│   └── lib/api.ts                # API client
├── agentcore-cba/                # Bedrock AgentCore agent
│   └── cbaindicatoragent/
│       ├── src/                  # Agent source code
│       │   ├── main.py           # Agent entrypoint
│       │   └── kb_tool.py        # Knowledge Base tools
│       ├── cdk/                  # CDK infrastructure
│       └── Dockerfile            # Container definition
├── lambda_function.py            # API Lambda handler
├── lambda_requirements.txt       # Lambda dependencies
├── scripts/                      # Build scripts
│   ├── build_lambda_layer.sh     # Lambda layer (Linux/Mac)
│   └── build_lambda_layer.ps1    # Lambda layer (Windows)
├── tests/                        # Test suite
├── pyproject.toml                # Python dependencies
├── DEPLOYMENT.md                 # Deployment guide
├── ARCHITECTURE.md               # Architecture documentation
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

## Deployment

For full deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Quick Deploy

```bash
# 1. Deploy AgentCore (CDK)
cd agentcore-cba/cbaindicatoragent/cdk
npm install && npm run cdk:deploy

# 2. Deploy Lambda
zip lambda_function.zip lambda_function.py
aws lambda update-function-code --function-name cba-indicator-api --zip-file fileb://lambda_function.zip

# 3. Deploy Frontend
cd cba-frontend
npm install && vercel --prod
```

### Required AWS Resources

- **Bedrock AgentCore Runtime** - Containerized Strands agent
- **Lambda Function** - API request handler  
- **API Gateway** - HTTP endpoints (`/chat`, `/upload`, `/recommendations`)
- **S3 Bucket** - File upload storage
- **Knowledge Base** - CBA indicators (ID: `0ZQBMXEKDI`)
