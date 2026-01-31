# CBA Indicator Selection Assistant - Deployment Guide

This guide covers deploying the CBA Indicator Selection Assistant.

## Table of Contents

- [Hackathon Quick Start](#hackathon-quick-start) - **Start here for demos**
- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [1. Local Development](#1-local-development)
- [2. AgentCore Deployment (CDK)](#2-agentcore-deployment-cdk)
- [3. Lambda Function Deployment](#3-lambda-function-deployment)
- [4. Frontend Deployment](#4-frontend-deployment)
- [5. Environment Variables Reference](#5-environment-variables-reference)
- [6. Post-Deployment Verification](#6-post-deployment-verification)
- [7. Troubleshooting](#7-troubleshooting)

---

## Hackathon Quick Start

**Goal:** Run the frontend locally on your laptop using the pre-deployed AWS backend.  
**You do NOT need AWS credentials for this section.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HACKATHON SETUP                                     │
│                                                                             │
│   ┌──────────────┐                      ┌─────────────────────────────────┐ │
│   │   LAPTOP     │                      │           AWS CLOUD             │ │
│   │              │                      │                                 │ │
│   │  Next.js     │  ───── HTTPS ─────►  │  API Gateway → Lambda →        │ │
│   │  Frontend    │                      │  AgentCore → Knowledge Base    │ │
│   │  (localhost) │  ◄──── JSON ──────   │                                 │ │
│   │              │                      │                                 │ │
│   └──────────────┘                      └─────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Step 0: Check Node.js

```bash
node -v
```

You must see **v18.18+** (or v20+). If not, install/update Node.js first.

### Step 1: Clone the Repository (skip if already cloned)

```bash
git clone https://github.com/CircularBioeconomyAlliance/coffee-recipe.git
cd coffee-recipe
```

### Step 2: Install Frontend Dependencies

```bash
cd cba-frontend
npm install
```

### Step 3: Run the Frontend

```bash
npm run dev
```

**Open:** http://localhost:3000  
You should see the landing page within 5-10 seconds.

**Default backend URL (pre-deployed):**  
`https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod`

### If Chat Shows "Sorry, I encountered an error"

This means the backend is **not responding** or the API URL is wrong.

Quick check:
```bash
curl -X POST https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
```

If this fails, the AWS backend is down or not deployed.

### What’s Running Where?

| Component | Location | URL |
|-----------|----------|-----|
| **Frontend** | Your laptop | http://localhost:3000 |
| **API Gateway** | AWS | https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod |
| **Lambda** | AWS | Handles `/chat`, `/upload`, `/recommendations` |
| **AgentCore** | AWS | Strands agent with Claude Sonnet |
| **Knowledge Base** | AWS | 801 methods, 224 indicators |

### Demo Flow

1. **Landing Page** → Choose "Chat" or "Upload Document"
2. **Chat** → Answer 4 questions (location, commodity, budget, outcomes)
3. **Results** → View recommended indicators and methods
4. **Compare** → Compare indicators side-by-side

**Upload note:** PDF only (max 10MB).

### Using Your Own Backend (Optional)

Set the API URL before running:

**macOS/Linux:**
```bash
export NEXT_PUBLIC_API_URL=https://your-api-id.execute-api.us-west-2.amazonaws.com/prod
npm run dev
```

**Windows PowerShell:**
```powershell
$env:NEXT_PUBLIC_API_URL="https://your-api-id.execute-api.us-west-2.amazonaws.com/prod"
npm run dev
```

**Windows CMD:**
```cmd
set NEXT_PUBLIC_API_URL=https://your-api-id.execute-api.us-west-2.amazonaws.com/prod
npm run dev
```

---

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 18.18+ | Frontend and CDK |
| Docker | Latest | AgentCore container builds |
| AWS CLI | 2.x | AWS deployments |
| uv | Latest | Python package management |

**If you are only doing Hackathon Quick Start:** you only need **Node.js**.

### Verify Tools Are Installed (copy/paste)

```bash
node -v
npm -v
python --version
aws --version
docker --version
uv --version
```

If any command says **"not found"**, install that tool before continuing.

### AWS Access Requirements

You need an AWS account with access to:

- **Amazon Bedrock** - Claude model access (request via AWS Console)
- **Amazon Bedrock AgentCore** - Agent runtime
- **Amazon Bedrock Knowledge Base** - CBA indicators KB (ID: `0ZQBMXEKDI`)
- **Amazon S3** - File upload storage
- **AWS Lambda** - API handlers
- **Amazon API Gateway** - HTTP endpoints
- **Amazon ECR** - Docker image registry

**Set your default region (recommended):**
```bash
aws configure set region us-west-2
```

### Request Bedrock Model Access

Before deploying, ensure you have access to Claude models:

1. Open the [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock)
2. Navigate to **Model access** in the sidebar
3. Click **Manage model access**
4. Select **Anthropic Claude** models (Claude Sonnet 4)
5. Click **Request model access**

### Confirm AWS Credentials (Required for Deployment)

```bash
aws sts get-caller-identity
```

You must see your AWS account ID. If this fails, **stop and fix credentials** before proceeding.

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│   Next.js       │────▶│   API Gateway    │────▶│   Lambda Function  │
│   Frontend      │     │   (HTTP API)     │     │   (Router)         │
└─────────────────┘     └──────────────────┘     └─────────┬──────────┘
                                                           │
                        ┌──────────────────────────────────┼──────────────┐
                        │                                  │              │
                        ▼                                  ▼              ▼
              ┌─────────────────┐              ┌──────────────┐   ┌──────────┐
              │ AgentCore       │              │   S3         │   │ Bedrock  │
              │ Runtime         │              │   (Uploads)  │   │ (Claude) │
              │ (Strands Agent) │              └──────────────┘   └──────────┘
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Knowledge Base  │
              │ (Indicators)    │
              └─────────────────┘
```

---

## 1. Local Development

### Frontend (Next.js)

```bash
cd cba-frontend

# Install dependencies
npm install

# Set API URL for local development (choose your OS)
export NEXT_PUBLIC_API_URL=https://your-api-gateway-url.execute-api.us-west-2.amazonaws.com/prod

# Run development server
npm run dev
```

**Windows PowerShell:**
```powershell
$env:NEXT_PUBLIC_API_URL="https://your-api-gateway-url.execute-api.us-west-2.amazonaws.com/prod"
npm run dev
```

**Windows CMD:**
```cmd
set NEXT_PUBLIC_API_URL=https://your-api-gateway-url.execute-api.us-west-2.amazonaws.com/prod
npm run dev
```

Opens at `http://localhost:3000`

---

## 2. AgentCore Deployment (CDK)

The AgentCore agent runs in a Docker container on Bedrock AgentCore Runtime.

### Step 1: Navigate to CDK Directory

```bash
cd agentcore-cba/cbaindicatoragent/cdk
```

### Step 2: Install CDK Dependencies

```bash
npm install
```

### Step 3: Bootstrap CDK (First Time Only)

```bash
npx cdk bootstrap aws://<ACCOUNT_ID>/<REGION>
```

### Step 4: Synthesize and Deploy

```bash
# Synthesize CloudFormation templates
npm run cdk synth

# Deploy all stacks
npm run cdk:deploy
```

This creates:
- **ECR Repository** - Docker image storage
- **AgentCore Runtime** - Container-based agent
- **AgentCore Gateway** - MCP protocol endpoint
- **AgentCore Memory** - Session storage (30-day TTL)
- **Cognito User Pool** - JWT authentication

### Step 5: Note the Output ARNs

After deployment, note these values from the CDK output:

```
AgentCoreStack.RuntimeArn = arn:aws:bedrock-agentcore:us-west-2:XXXX:runtime/cbaindicatoragent_Agent-XXXX
AgentCoreStack.GatewayUrl = https://XXXX.execute-api.us-west-2.amazonaws.com
```

### Test AgentCore Deployment

```bash
# From the agentcore-cba/cbaindicatoragent directory
agentcore invoke '{"prompt": "What indicators do you have for coffee projects in Brazil?"}'
```

---

## 3. Lambda Function Deployment

The Lambda function (`lambda_function.py`) handles API requests and routes to AgentCore.

### Step 0: Set Your Values (replace placeholders)

You will use these values repeatedly:

- `<ACCOUNT_ID>`: Your AWS account ID  
  ```bash
  aws sts get-caller-identity --query Account --output text
  ```
- `<REGION>`: Use `us-west-2` unless you deployed elsewhere
- `<UPLOAD_BUCKET>`: Must be globally unique (example: `cba-indicator-uploads-<ACCOUNT_ID>`)

### Step 1: Build Lambda Layer

The Lambda requires `pypdf` for PDF processing. Build a layer:

**On Linux/Mac:**
```bash
chmod +x scripts/build_lambda_layer.sh
./scripts/build_lambda_layer.sh
```

**On Windows (PowerShell):**
```powershell
.\scripts\build_lambda_layer.ps1
```

**Using Docker (Recommended for Lambda Compatibility):**
```bash
docker run --rm -v ${PWD}:/var/task public.ecr.aws/sam/build-python3.12 \
  pip install -r lambda_requirements.txt -t lambda_layer/python

cd lambda_layer && zip -r ../cba-lambda-dependencies.zip python/
```

### Step 2: Publish Lambda Layer

```bash
aws lambda publish-layer-version \
  --layer-name cba-lambda-dependencies \
  --zip-file fileb://cba-lambda-dependencies.zip \
  --compatible-runtimes python3.12 python3.11 \
  --compatible-architectures x86_64
```

Note the `LayerVersionArn` from the output.

### Step 3: Create the Lambda IAM Role (one-time)

1) Create a trust policy file `lambda-trust-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "lambda.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

2) Create the role and attach basic logging:
```bash
aws iam create-role \
  --role-name cba-lambda-role \
  --assume-role-policy-document file://lambda-trust-policy.json

aws iam attach-role-policy \
  --role-name cba-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

3) Attach permissions for S3 + Bedrock + AgentCore:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["s3:PutObject"], "Resource": "arn:aws:s3:::<UPLOAD_BUCKET>/*" },
    { "Effect": "Allow", "Action": ["bedrock:InvokeModel"], "Resource": "*" },
    { "Effect": "Allow", "Action": ["bedrock-agentcore:InvokeAgentRuntime"], "Resource": "*" }
  ]
}
```

Save this as `lambda-policy.json`, then run:
```bash
aws iam put-role-policy \
  --role-name cba-lambda-role \
  --policy-name cba-lambda-inline \
  --policy-document file://lambda-policy.json
```

### Step 4: Create or Update the Lambda Function

**Create the Lambda function:**

```bash
# Zip the Lambda code
zip lambda_function.zip lambda_function.py

# Create function
aws lambda create-function \
  --function-name cba-indicator-api \
  --runtime python3.12 \
  --role arn:aws:iam::<ACCOUNT_ID>:role/cba-lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_function.zip \
  --timeout 60 \
  --memory-size 512 \
  --layers <LAYER_VERSION_ARN> \
  --environment "Variables={BEDROCK_AGENTCORE_ARN=<AGENTCORE_RUNTIME_ARN>,UPLOAD_BUCKET_NAME=<UPLOAD_BUCKET>,AWS_REGION=<REGION>}"
```

**Or update existing function:**

```bash
zip lambda_function.zip lambda_function.py

aws lambda update-function-code \
  --function-name cba-indicator-api \
  --zip-file fileb://lambda_function.zip
```

If you need to update environment variables or layers later:
```bash
aws lambda update-function-configuration \
  --function-name cba-indicator-api \
  --layers <LAYER_VERSION_ARN> \
  --environment "Variables={BEDROCK_AGENTCORE_ARN=<AGENTCORE_RUNTIME_ARN>,UPLOAD_BUCKET_NAME=<UPLOAD_BUCKET>,AWS_REGION=<REGION>}"
```

### Step 5: Create S3 Bucket for Uploads

```bash
aws s3 mb s3://<UPLOAD_BUCKET> --region <REGION>
```

### Step 6: Create API Gateway (HTTP API)

**macOS/Linux:**
```bash
# Create HTTP API
API_ID=$(aws apigatewayv2 create-api \
  --name cba-indicator-api \
  --protocol-type HTTP \
  --cors-configuration AllowOrigins="*",AllowMethods="GET,POST,OPTIONS",AllowHeaders="Content-Type" \
  --query ApiId --output text)

# Create Lambda integration
INTEGRATION_ID=$(aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:<REGION>:<ACCOUNT_ID>:function:cba-indicator-api \
  --payload-format-version 2.0 \
  --query IntegrationId --output text)

# Create routes
aws apigatewayv2 create-route --api-id $API_ID --route-key "POST /chat" --target integrations/$INTEGRATION_ID
aws apigatewayv2 create-route --api-id $API_ID --route-key "POST /upload" --target integrations/$INTEGRATION_ID
aws apigatewayv2 create-route --api-id $API_ID --route-key "GET /recommendations" --target integrations/$INTEGRATION_ID
aws apigatewayv2 create-route --api-id $API_ID --route-key "OPTIONS /{proxy+}" --target integrations/$INTEGRATION_ID

# Create stage
aws apigatewayv2 create-stage --api-id $API_ID --stage-name prod --auto-deploy
```

**Windows PowerShell:**
```powershell
$apiId = aws apigatewayv2 create-api `
  --name cba-indicator-api `
  --protocol-type HTTP `
  --cors-configuration AllowOrigins="*",AllowMethods="GET,POST,OPTIONS",AllowHeaders="Content-Type" `
  --query ApiId --output text

$integrationId = aws apigatewayv2 create-integration `
  --api-id $apiId `
  --integration-type AWS_PROXY `
  --integration-uri arn:aws:lambda:<REGION>:<ACCOUNT_ID>:function:cba-indicator-api `
  --payload-format-version 2.0 `
  --query IntegrationId --output text

aws apigatewayv2 create-route --api-id $apiId --route-key "POST /chat" --target integrations/$integrationId
aws apigatewayv2 create-route --api-id $apiId --route-key "POST /upload" --target integrations/$integrationId
aws apigatewayv2 create-route --api-id $apiId --route-key "GET /recommendations" --target integrations/$integrationId
aws apigatewayv2 create-route --api-id $apiId --route-key "OPTIONS /{proxy+}" --target integrations/$integrationId

aws apigatewayv2 create-stage --api-id $apiId --stage-name prod --auto-deploy
```

Your API URL is:
```
https://<API_ID>.execute-api.<REGION>.amazonaws.com/prod
```

### Step 7: Configure Lambda Permissions

```bash
# Allow API Gateway to invoke Lambda
aws lambda add-permission \
  --function-name cba-indicator-api \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:<REGION>:<ACCOUNT_ID>:<API_ID>/*/*"
```

If you see `ResourceConflictException`, the permission already exists.

---

## 4. Frontend Deployment

### Option A: Vercel (Recommended)

```bash
cd cba-frontend

# Install Vercel CLI
npm i -g vercel

# Link and deploy (first time)
vercel

# Set environment variable BEFORE production deploy
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-api-id.execute-api.us-west-2.amazonaws.com/prod

# Deploy to production
vercel --prod
```

### Option B: AWS Amplify

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize Amplify
amplify init

# Add hosting
amplify add hosting

# Set environment variable in Amplify Console:
# NEXT_PUBLIC_API_URL = https://your-api-id.execute-api.us-west-2.amazonaws.com/prod

# Deploy
amplify publish
```

### Option C: Static Export to S3 + CloudFront

```bash
cd cba-frontend

# Set API URL for the build
export NEXT_PUBLIC_API_URL=https://your-api-id.execute-api.us-west-2.amazonaws.com/prod

# Build static export
npm run build

# Sync to S3
aws s3 sync out/ s3://cba-frontend-bucket --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id XXXX --paths "/*"
```

**Windows PowerShell:**
```powershell
$env:NEXT_PUBLIC_API_URL="https://your-api-id.execute-api.us-west-2.amazonaws.com/prod"
npm run build
```

---

## 5. Environment Variables Reference

### Lambda Function

| Variable | Description | Example |
|----------|-------------|---------|
| `BEDROCK_AGENTCORE_ARN` | AgentCore Runtime ARN | `arn:aws:bedrock-agentcore:us-west-2:123456:runtime/cbaindicatoragent_Agent-xxx` |
| `UPLOAD_BUCKET_NAME` | S3 bucket for uploads | `cba-indicator-uploads` |
| `AWS_REGION` | AWS region | `us-west-2` |

### AgentCore Container

| Variable | Description | Example |
|----------|-------------|---------|
| `KNOWLEDGE_BASE_ID` | Bedrock KB ID | `0ZQBMXEKDI` |
| `AWS_REGION` | AWS region | `us-west-2` |
| `BEDROCK_AGENTCORE_MEMORY_ID` | Memory resource ID | (auto-set by CDK) |

### Frontend (Next.js)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | API Gateway URL | `https://xxx.execute-api.us-west-2.amazonaws.com/prod` |

### Local Development

| Variable | Description | Required |
|----------|-------------|----------|
| `AWS_DEFAULT_REGION` | AWS region | Yes |
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes |
| `AWS_SESSION_TOKEN` | Session token | If using temporary credentials |

---

## 6. Post-Deployment Verification

### Test API Endpoints

**Chat endpoint:**
```bash
curl -X POST https://YOUR_API_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What indicators do you have for coffee projects?"}'
```

You should see JSON with `response` and `session_id`.

**Recommendations endpoint:**
```bash
curl "https://YOUR_API_URL/recommendations?session_id=test-session"
```

You should see JSON with `indicators` (possibly empty).

### Test AgentCore

```bash
agentcore invoke '{"prompt": "Hello, what can you help me with?"}'
```

### Test Frontend

1. Open the frontend URL
2. Navigate to Chat page
3. Send a test message
4. Verify response is received

---

## 7. Troubleshooting

### Hackathon/Local Frontend Issues

#### Frontend can't connect to API

1. **Check internet connection** - The frontend needs to reach AWS
2. **Test API directly:**
   ```bash
   curl -X POST https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "hello"}'
   ```
3. **Check browser console** - Look for CORS or network errors
4. **Disable VPN/proxy** - Corporate networks may block the API

#### "Failed to fetch" errors

- The AWS backend may be cold-starting (wait 10-15 seconds, retry)
- Lambda has a 60-second timeout for longer conversations

#### Chat responses are slow

- First request after inactivity takes longer (cold start)
- Complex queries searching the Knowledge Base take 5-15 seconds
- This is normal for RAG-based AI systems

#### Upload not working

- File must be a PDF
- Maximum file size: 10MB
- The backend extracts text and sends to Claude for parsing

#### "Unknown route" from API

- Your API Gateway routes were not created or are pointing to the wrong integration
- Re-run the **Create API Gateway** step and confirm `/chat`, `/upload`, `/recommendations` routes exist

### Backend Deployment Issues

#### "Model access denied"

Request access to Claude models in the Bedrock Console:
1. Go to **Bedrock Console** → **Model access**
2. Request access to Anthropic Claude models

#### "Knowledge Base not found"

Verify the Knowledge Base ID is correct:
```bash
aws bedrock-agent list-knowledge-bases --region us-west-2
```

#### "Lambda timeout"

Increase Lambda timeout to 60 seconds:
```bash
aws lambda update-function-configuration \
  --function-name cba-indicator-api \
  --timeout 60
```

#### "CORS errors in frontend"

Verify API Gateway CORS configuration:
```bash
aws apigatewayv2 get-api --api-id YOUR_API_ID
```

#### "PDF extraction failed"

Ensure Lambda layer includes `pypdf`:
```bash
aws lambda get-function --function-name cba-indicator-api
# Check Layers array includes the pypdf layer
```

### Logs

**Lambda logs:**
```bash
aws logs tail /aws/lambda/cba-indicator-api --follow
```

**AgentCore logs:**
```bash
# View in CloudWatch Logs
aws logs tail /aws/bedrock-agentcore/cbaindicatoragent --follow
```

---

## Quick Reference Commands

```bash
# Deploy AgentCore
cd agentcore-cba/cbaindicatoragent/cdk && npm run cdk:deploy

# Update Lambda code
zip lambda_function.zip lambda_function.py && \
aws lambda update-function-code --function-name cba-indicator-api --zip-file fileb://lambda_function.zip

# Deploy frontend (Vercel)
cd cba-frontend && vercel --prod

# View Lambda logs
aws logs tail /aws/lambda/cba-indicator-api --follow

# Test chat endpoint
curl -X POST https://YOUR_API_URL/chat -H "Content-Type: application/json" -d '{"message": "test"}'
```
