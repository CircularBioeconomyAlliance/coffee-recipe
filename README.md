# CBA Indicator Selection Assistant

An AI-powered tool for the Circular Bioeconomy Alliance (CBA) that helps users discover and select monitoring & evaluation indicators from the CBA M&E Framework. Built with [Strands Agents](https://github.com/strands-agents/strands-agents), Amazon Bedrock AgentCore, and Claude.

**Status:** Demo Ready | **Knowledge Base:** 801 methods, 224 indicators

---

## Quick Start (Hackathon Demo)

The backend is **already deployed on AWS**. Just run the frontend:

```bash
git clone https://github.com/CircularBioeconomyAlliance/coffee-recipe.git
cd coffee-recipe/cba-frontend
npm install
npm run dev
```

Open **http://localhost:3000** - you're ready to demo!

> **No AWS credentials needed** for the frontend demo. The pre-deployed backend handles everything.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PRODUCTION STACK                                │
│                                                                             │
│   ┌──────────────┐         ┌──────────────────────────────────────────────┐ │
│   │   Browser    │         │                  AWS Cloud                   │ │
│   │              │         │                                              │ │
│   │  Next.js     │ HTTPS   │  ┌─────────┐   ┌────────┐   ┌─────────────┐ │ │
│   │  Frontend    │────────►│  │   API   │──►│ Lambda │──►│  AgentCore  │ │ │
│   │ (localhost)  │         │  │ Gateway │   │        │   │  (Strands)  │ │ │
│   │              │◄────────│  └─────────┘   └────────┘   └──────┬──────┘ │ │
│   └──────────────┘  JSON   │                                    │        │ │
│                            │                             ┌──────▼──────┐ │ │
│                            │                             │  Knowledge  │ │ │
│                            │                             │    Base     │ │ │
│                            │                             │ (Bedrock)   │ │ │
│                            │                             └─────────────┘ │ │
│                            └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Component | Technology | Description |
|-----------|------------|-------------|
| **Frontend** | Next.js 15, React 19, Tailwind CSS | Modern UI with CBA branding |
| **API** | AWS API Gateway + Lambda | Routes `/chat`, `/upload`, `/recommendations` |
| **Agent** | Strands Agents on Bedrock AgentCore | Claude Sonnet 4 with KB tools |
| **Knowledge Base** | Amazon Bedrock KB | 801 methods, 224 indicators from CBA M&E Framework |

---

## Demo Flow

1. **Landing Page** (`/`) - Choose "Upload Document" or "Start Chat"
2. **Upload** (`/upload`) - Drag & drop a project PDF, AI extracts key details
3. **Chat** (`/chat`) - Conversational project builder with live profile sidebar
4. **Results** (`/results`) - Recommended indicators with filtering
5. **Compare** (`/compare`) - Side-by-side indicator comparison

---

## Documentation

| Document | Purpose |
|----------|---------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Full deployment guide (start with Hackathon Quick Start) |
| [PRESENTER_GUIDE.md](PRESENTER_GUIDE.md) | Talking points and demo script |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture diagrams |
| [CODE_REVIEW.md](CODE_REVIEW.md) | Code review notes |
| [CLAUDE.md](CLAUDE.md) | AI assistant context file |

---

## Project Structure

```
coffee-recipe/
├── cba-frontend/                 # Next.js frontend
│   ├── app/
│   │   ├── page.tsx              # Landing page
│   │   ├── chat/page.tsx         # Chat interface
│   │   ├── upload/page.tsx       # PDF upload
│   │   ├── results/page.tsx      # Indicator cards
│   │   └── compare/page.tsx      # Side-by-side comparison
│   └── lib/api.ts                # API client
│
├── lambda_function.py            # AWS Lambda handler
│                                 # Routes: /chat, /upload, /recommendations
│
├── agentcore-cba/                # Bedrock AgentCore agent
│   └── cbaindicatoragent/
│       ├── src/
│       │   ├── main.py           # Agent entrypoint with Strands
│       │   └── kb_tool.py        # Knowledge Base search tools
│       └── cdk/                  # CDK deployment infrastructure
│
├── cba_inputs/                   # Reference documents (PDFs, Excel)
├── scripts/                      # Build scripts (Lambda layer)
└── tests/                        # Test suite
```

---

## Pre-Deployed Backend

The production backend is already running:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod/chat` | POST | Chat with agent |
| `https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod/upload` | POST | Upload PDF |
| `https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod/recommendations` | GET | Get indicators |

**Test the backend:**
```bash
curl -X POST https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
```

---

## Development Setup

For local development with your own AWS resources:

### Prerequisites

- Node.js 18.18+ (frontend)
- Python 3.12+ (agent development)
- AWS credentials with Bedrock access

### Frontend Development

```bash
cd cba-frontend
npm install
npm run dev                    # Uses pre-deployed backend by default

# Or connect to your own backend:
NEXT_PUBLIC_API_URL=https://your-api.execute-api.us-west-2.amazonaws.com/prod npm run dev
```

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions.

**Quick Deploy:**

```bash
# 1. Deploy AgentCore agent
cd agentcore-cba/cbaindicatoragent/cdk
npm install && npm run cdk:deploy

# 2. Update Lambda
zip lambda_function.zip lambda_function.py
aws lambda update-function-code --function-name cba-indicator-api --zip-file fileb://lambda_function.zip

# 3. Build frontend for static hosting
cd cba-frontend
npm run build    # Creates static export in 'out/' folder
```

---

## AWS Resources

| Resource | ID/ARN | Purpose |
|----------|--------|---------|
| **Knowledge Base** | `0ZQBMXEKDI` | CBA M&E indicators and methods |
| **AgentCore Runtime** | `cbaindicatoragent_Agent-buoE288RIT` | Strands agent with Claude |
| **S3 Upload Bucket** | `cba-indicator-uploads` | PDF file storage |
| **API Gateway** | `pjuuem2fn8` | HTTP API endpoint |

---

## Known Limitations

- **In-memory recommendations**: Lambda stores recommendations in memory; lost on cold start
- **PDF only**: Upload accepts PDF files only (no Excel)
- **Export disabled**: Export buttons are placeholder (coming soon)
- **Profile heuristics**: Chat sidebar uses keyword matching to track profile state

---

## Running Tests

```bash
cd cba-frontend
npm run lint                   # TypeScript/ESLint checks
npm run build                  # Verify production build
```

---

## License

Copyright 2024 Circular Bioeconomy Alliance. All rights reserved.
