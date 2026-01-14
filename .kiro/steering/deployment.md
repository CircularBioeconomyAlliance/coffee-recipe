# Deploying CBA Agent to Amazon Bedrock AgentCore Runtime

This guide covers deploying the CBA Indicator Selection Assistant to Amazon Bedrock AgentCore Runtime using the SDK Integration approach.

## Overview

The CBA agent is deployed using the Bedrock AgentCore Runtime Python SDK, which provides a lightweight wrapper for deploying Strands agents as HTTP services.

## Prerequisites

- Python 3.10+
- AWS account with appropriate permissions
- AWS credentials configured
- Docker, Finch, or Podman (optional, for local testing only)

## Quick Start

### 1. Install Dependencies

```bash
uv sync
uv add bedrock-agentcore bedrock-agentcore-starter-toolkit
```

### 2. Test Locally

Run the agent locally to verify it works:

```bash
uv run src/bedrock_agent.py
```

Test with curl:

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the key principles of circular bioeconomy?"}'
```

### 3. Deploy to AWS

#### Option A: Using Starter Toolkit (Recommended)

```bash
# Configure the agent
uv run agentcore configure --entrypoint src/bedrock_agent.py

# Optional: Test locally with container (requires Docker/Finch/Podman)
uv run agentcore launch --local

# Deploy to AWS
uv run agentcore launch

# Test the deployed agent
uv run agentcore invoke '{"prompt": "Hello from Bedrock!"}'
```

#### Option B: Manual Deployment

1. **Build and push container to ECR:**

```bash
# Create ECR repository
aws ecr create-repository --repository-name cba-agent --region us-west-2

# Login to ECR
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Build and push (requires Dockerfile - see Custom Implementation section)
docker buildx build --platform linux/arm64 \
  -t <account-id>.dkr.ecr.us-west-2.amazonaws.com/cba-agent:latest --push .
```

2. **Deploy using boto3:**

Update `deploy_agent.py` with your ECR URI and IAM role ARN, then run:

```bash
uv run deploy_agent.py
```

### 4. Invoke the Deployed Agent

Update `invoke_agent.py` with your agent ARN, then run:

```bash
uv run invoke_agent.py
```

## Project Structure

```
coffee-recipe/
├── src/
│   ├── bedrock_agent.py      # AgentCore Runtime entrypoint
│   ├── agent.py               # CLI chatbot
│   ├── app.py                 # Streamlit web UI
│   └── config.py              # Shared configuration
├── deploy_agent.py            # Deployment script
├── invoke_agent.py            # Invocation test script
├── requirements.txt           # Deployment dependencies
└── pyproject.toml             # Project dependencies
```

## Agent Payload Format

### Request

```json
{
  "prompt": "Your question here",
  "file_content": "Optional document content for context"
}
```

### Response

```json
{
  "result": "Agent response text",
  "status": "success"
}
```

## Configuration

The agent uses the following configuration from `src/config.py`:

- **Model**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- **Knowledge Base ID**: `0ZQBMXEKDI`
- **Region**: `us-west-2`
- **Temperature**: `0.2` (deterministic responses)

## IAM Permissions

Your IAM role needs permissions for:

- Amazon Bedrock model invocation
- Amazon Bedrock Knowledge Base access
- CloudWatch Logs (for monitoring)

Example policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:Retrieve"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## Troubleshooting

### Local Testing Issues

**Problem**: Agent fails to start locally
- **Solution**: Verify AWS credentials are set in environment variables
- Check that `STRANDS_KNOWLEDGE_BASE_ID` is configured

**Problem**: Import errors
- **Solution**: Run `uv sync` to ensure all dependencies are installed

### Deployment Issues

**Problem**: Container build fails
- **Solution**: Ensure Docker/Finch/Podman is running (only needed for local testing)
- For AWS deployment, starter toolkit handles containerization

**Problem**: Agent runtime creation fails
- **Solution**: Verify IAM role has correct permissions
- Check that ECR image URI is correct (manual deployment only)

### Runtime Issues

**Problem**: Agent returns errors
- **Solution**: Check CloudWatch logs for detailed error messages
- Verify Knowledge Base ID is correct
- Ensure model ID is available in your region

**Problem**: Slow responses
- **Solution**: Consider increasing agent runtime resources
- Check Knowledge Base query performance

## Advanced: Custom Implementation

For full control over the HTTP interface, you can implement a custom FastAPI server instead of using the SDK wrapper. This approach is documented in the full Bedrock AgentCore Runtime deployment guide but requires:

1. Creating a custom `Dockerfile` for ARM64
2. Implementing `/invocations` POST and `/ping` GET endpoints
3. Manual container build and ECR push
4. More complex deployment configuration

The SDK Integration approach (used in `src/bedrock_agent.py`) is recommended for most use cases as it handles these details automatically.

## Monitoring and Observability

After deployment, monitor your agent using:

- **CloudWatch Logs**: View agent execution logs
- **CloudWatch Metrics**: Track invocation counts, latency, errors
- **AWS X-Ray**: Trace requests through the system (if enabled)

## Next Steps

1. Set up CloudWatch alarms for error rates
2. Configure auto-scaling based on load
3. Implement request/response logging
4. Add custom metrics for business KPIs
5. Set up CI/CD pipeline for automated deployments

## Resources

- [Strands Agents Documentation](https://github.com/strands-agents/strands-agents)
- [Bedrock AgentCore Runtime Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
