# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start (Hackathon Demo)

```bash
# Run the production frontend (connects to pre-deployed AWS backend)
cd cba-frontend
npm install
npm run dev
# Open http://localhost:3000
```

## Project Structure

```
coffee-recipe/
├── cba-frontend/                 # Production Next.js frontend
│   ├── app/
│   │   ├── page.tsx              # Landing page
│   │   ├── chat/page.tsx         # Chat interface
│   │   ├── upload/page.tsx       # PDF upload
│   │   ├── results/page.tsx      # Indicator recommendations
│   │   └── compare/page.tsx      # Side-by-side comparison
│   └── lib/api.ts                # API client
├── lambda_function.py            # AWS Lambda API handler
├── agentcore-cba/                # Bedrock AgentCore agent
│   └── cbaindicatoragent/
│       ├── src/
│       │   ├── main.py           # Agent entry point (includes profile tools)
│       │   └── kb_tool.py        # Knowledge Base search tools
│       └── cdk/                  # CDK deployment
├── DEPLOYMENT.md                 # Full deployment guide
├── CODE_REVIEW.md                # Architecture review
└── PRESENTER_GUIDE.md            # Demo walkthrough
```

## Architecture

**Production stack:**
```
Next.js Frontend → API Gateway → Lambda → AgentCore → Knowledge Base
     (local)          (AWS)       (AWS)     (AWS)        (AWS)
```

### Frontend (`cba-frontend/`)

- **Framework:** Next.js 15 with React 19, TypeScript
- **Styling:** Tailwind CSS with CBA branding (#031f35 navy, #FBAD17 gold)
- **Animations:** Framer Motion
- **API URL:** Defaults to pre-deployed AWS backend; override with `NEXT_PUBLIC_API_URL`

Key pages:
- `/` - Landing with Upload/Chat entry points
- `/chat` - Conversational project builder with profile sidebar
- `/upload` - PDF drag-and-drop with auto-extraction
- `/results` - Indicator cards with filtering
- `/compare` - Side-by-side indicator comparison

### Lambda (`lambda_function.py`)

Routes:
- `POST /chat` - Proxies to AgentCore, extracts indicators from response
- `POST /upload` - Stores PDF to S3, extracts text with pypdf, analyzes with Claude
- `GET /recommendations?session_id=xxx` - Returns stored indicator recommendations

Environment variables:
- `BEDROCK_AGENTCORE_ARN` - AgentCore runtime ARN
- `UPLOAD_BUCKET_NAME` - S3 bucket for PDF uploads
- `AWS_REGION` - AWS region (default: us-west-2)

### AgentCore Agent (`agentcore-cba/`)

- **Framework:** Strands Agents on Bedrock AgentCore
- **Model:** Claude Sonnet 4
- **Knowledge Base:** 801 methods, 224 indicators (ID: `0ZQBMXEKDI`)

Tools:
- `search_cba_indicators()` - General indicator search
- `search_indicators_by_outcome()` - Outcome-aligned search
- `search_methods_by_budget()` - Budget-appropriate methods
- `search_location_specific_indicators()` - Region-specific search
- `set_project_*()` / `get_project_profile()` - Profile management

## Commands

```bash
# Frontend (production)
cd cba-frontend
npm install
npm run dev          # Development server at localhost:3000
npm run build        # Production build

# Deploy AgentCore
cd agentcore-cba/cbaindicatoragent/cdk
npm install
npm run cdk:deploy

# Update Lambda
zip lambda_function.zip lambda_function.py
aws lambda update-function-code --function-name cba-indicator-api --zip-file fileb://lambda_function.zip
```

## API Patterns

### Chat Request
```typescript
POST /chat
{
  "message": "I have a coffee project in Brazil",
  "session_id": "session-123",
  "profile": { "location": "Brazil" }
}
// Response: { "response": "...", "session_id": "...", "has_recommendations": true }
```

### Upload Request
```typescript
POST /upload
Content-Type: application/octet-stream
Body: <base64-encoded PDF>
// Response: { "found": { "location": "...", "commodity": "..." }, "missing": [...] }
```

### Recommendations Request
```typescript
GET /recommendations?session_id=session-123
// Response: { "indicators": [...], "session_id": "..." }
```

## Key Files to Edit

| Task | File(s) |
|------|---------|
| Change UI styling | `cba-frontend/tailwind.config.ts`, `app/globals.css` |
| Modify chat behavior | `cba-frontend/app/chat/page.tsx` |
| Update API routes | `lambda_function.py` |
| Change agent prompts | `agentcore-cba/cbaindicatoragent/src/main.py` |
| Add KB search tools | `agentcore-cba/cbaindicatoragent/src/kb_tool.py` |

## Known Limitations

- **In-memory recommendations:** Lambda stores recommendations in memory; lost on cold start
- **PDF only:** Upload accepts PDF files only (no Excel)
- **Export disabled:** Export buttons are placeholder (coming soon)
- **Profile heuristics:** Chat sidebar uses keyword matching to track profile state

## AWS Configuration

Required environment variables for local development with your own backend:
```bash
export NEXT_PUBLIC_API_URL=https://your-api.execute-api.us-west-2.amazonaws.com/prod
export AWS_DEFAULT_REGION=us-west-2
```

For the pre-deployed hackathon backend, no configuration is needed.
