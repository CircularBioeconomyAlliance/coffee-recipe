# CBA Indicator Selection Assistant - Architecture

This document describes the architecture of the CBA (Circular Bioeconomy Alliance) Indicator Selection Assistant.

## System Overview

```mermaid
flowchart TB
    subgraph Users["👤 Users"]
        CLI["CLI User"]
        Web["Web User"]
    end

    subgraph LocalDev["🖥️ Local Development"]
        CLI_Agent["agent.py<br/>(CLI Chatbot)"]
        Streamlit["app.py<br/>(Streamlit Web UI)"]
        Config["config.py<br/>(Shared Config)"]
        SystemPrompt["prompts/system.txt"]
    end

    subgraph Production["☁️ Production Deployment"]
        subgraph Frontend["Next.js Frontend"]
            ChatPage["chat/page.tsx"]
            UploadPage["upload/page.tsx"]
            ResultsPage["results/page.tsx"]
            ApiLib["lib/api.ts"]
        end

        subgraph Lambda["AWS Lambda"]
            Handler["lambda_function.py"]
            ChatHandler["/chat endpoint"]
            UploadHandler["/upload endpoint"]
        end

        subgraph AgentCore["Bedrock AgentCore"]
            MainAgent["main.py<br/>(Agent Entry)"]
            KBTool["kb_tool.py<br/>(KB Search Tools)"]
            ProfileTools["Project Profile Tools"]
        end
    end

    subgraph AWS["AWS Services"]
        Bedrock["Amazon Bedrock<br/>(Claude Sonnet 4.5)"]
        KB["Bedrock Knowledge Base<br/>(801 methods, 224 indicators)"]
        S3["S3 Bucket<br/>(File Uploads)"]
        APIGateway["API Gateway"]
    end

    subgraph Tools["🔧 Strands Agent Tools"]
        Memory["memory"]
        UseLLM["use_llm"]
        HTTPReq["http_request"]
        FileWrite["file_write"]
        CurrentTime["current_time"]
    end

    %% User flows
    CLI --> CLI_Agent
    Web --> Streamlit
    Web --> ChatPage

    %% Local development connections
    CLI_Agent --> Config
    Streamlit --> Config
    Config --> SystemPrompt
    CLI_Agent --> Bedrock
    Streamlit --> Bedrock

    %% Production flow
    ChatPage --> ApiLib
    UploadPage --> ApiLib
    ApiLib --> APIGateway
    APIGateway --> Handler
    Handler --> ChatHandler
    Handler --> UploadHandler
    ChatHandler --> AgentCore
    UploadHandler --> S3
    UploadHandler --> Bedrock

    %% AgentCore connections
    MainAgent --> KBTool
    MainAgent --> ProfileTools
    KBTool --> KB
    MainAgent --> Bedrock

    %% Tool connections
    CLI_Agent --> Tools
    Streamlit --> Tools
    MainAgent --> Tools

    %% KB Search functions
    KBTool -.-> |"search_cba_indicators()"| KB
    KBTool -.-> |"search_indicators_by_outcome()"| KB
    KBTool -.-> |"search_methods_by_budget()"| KB
    KBTool -.-> |"search_location_specific_indicators()"| KB

    classDef aws fill:#FF9900,stroke:#232F3E,color:#232F3E
    classDef frontend fill:#61DAFB,stroke:#20232A,color:#20232A
    classDef python fill:#3776AB,stroke:#FFD43B,color:#fff
    classDef tools fill:#4CAF50,stroke:#2E7D32,color:#fff

    class Bedrock,KB,S3,APIGateway aws
    class ChatPage,UploadPage,ResultsPage,ApiLib frontend
    class CLI_Agent,Streamlit,Handler,MainAgent,KBTool python
    class Memory,UseLLM,HTTPReq,FileWrite,CurrentTime tools
```

## Key Components

| Component | Purpose |
|-----------|---------|
| **`src/agent.py`** | CLI chatbot for local testing with PDF/Excel file parsing |
| **`src/app.py`** | Streamlit web UI with session management and file upload |
| **`src/config.py`** | Shared configuration (model ID, KB ID, system prompt) |
| **`cba-frontend/`** | Production Next.js frontend with modern UI |
| **`lambda_function.py`** | AWS Lambda handler routing `/chat` and `/upload` requests |
| **`agentcore-cba/`** | Bedrock AgentCore deployment with KB search tools |

## Production Request Flow (Lambda & API Gateway)

```mermaid
flowchart LR
    subgraph Browser["🌐 Browser"]
        NextJS["Next.js Frontend<br/>(chat/page.tsx)"]
    end

    subgraph APILayer["AWS API Gateway"]
        APIGW["API Gateway<br/>pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod"]
    end

    subgraph LambdaLayer["AWS Lambda"]
        Lambda["lambda_function.py"]
        Router{{"Route by path"}}
        ChatHandler["handle_chat()"]
        UploadHandler["handle_upload()"]
    end

    subgraph BedrockServices["AWS Bedrock"]
        AgentCore["Bedrock AgentCore<br/>(cbaindicatoragent)"]
        BedrockRuntime["Bedrock Runtime<br/>(Claude Sonnet 4.5)"]
        KB["Knowledge Base<br/>(Indicators & Methods)"]
    end

    subgraph Storage["AWS S3"]
        S3["cba-indicator-uploads<br/>bucket"]
    end

    NextJS -->|"POST /chat<br/>POST /upload"| APIGW
    APIGW -->|"Invoke"| Lambda
    Lambda --> Router
    Router -->|"/chat"| ChatHandler
    Router -->|"/upload"| UploadHandler
    
    ChatHandler -->|"invoke_agent_runtime()"| AgentCore
    AgentCore -->|"Query"| KB
    AgentCore -->|"LLM calls"| BedrockRuntime
    
    UploadHandler -->|"put_object()"| S3
    UploadHandler -->|"invoke_model()<br/>(extract profile)"| BedrockRuntime

    classDef gateway fill:#FF4F8B,stroke:#232F3E,color:#fff
    classDef lambda fill:#FF9900,stroke:#232F3E,color:#232F3E
    classDef bedrock fill:#01A88D,stroke:#232F3E,color:#fff
    classDef storage fill:#3F8624,stroke:#232F3E,color:#fff

    class APIGW gateway
    class Lambda,Router,ChatHandler,UploadHandler lambda
    class AgentCore,BedrockRuntime,KB bedrock
    class S3 storage
```

## Request Flow Details

### 1. Frontend → API Gateway

```typescript
// cba-frontend/lib/api.ts
const API_URL = "https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod";

// Chat request
fetch(`${API_URL}/chat`, { method: "POST", body: JSON.stringify({ message, session_id }) })

// Upload request  
fetch(`${API_URL}/upload`, { method: "POST", body: formData })
```

### 2. API Gateway → Lambda

API Gateway receives the HTTP request and invokes the Lambda function.

### 3. Lambda Routes the Request

```python
# lambda_function.py
def lambda_handler(event, context):
    path = event.get('rawPath', event.get('path', ''))
    
    if '/chat' in path:
        return handle_chat(event)      # → Bedrock AgentCore
    elif '/upload' in path:
        return handle_upload(event)    # → S3 + Bedrock Runtime
```

### 4a. Chat Flow: Lambda → AgentCore → Knowledge Base

```python
# handle_chat() calls AgentCore
response = agentcore.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-west-2:...:runtime/cbaindicatoragent_Agent-...',
    runtimeSessionId=session_id,
    payload=json.dumps({"prompt": message}).encode()
)
```

### 4b. Upload Flow: Lambda → S3 → Bedrock (extract profile)

```python
# handle_upload() stores file and extracts project info
s3.put_object(Bucket=UPLOAD_BUCKET, Key=file_key, Body=file_bytes)
bedrock_runtime.invoke_model(modelId='...claude...', body=prompt)  # Extract location, commodity, budget
```

## Data Flow Summary

1. **User Input** → User provides project details (location, commodity, budget, outcomes)
2. **Agent Processing** → Strands Agent with Claude Sonnet 4.5 processes the request
3. **KB Search** → Agent queries Bedrock Knowledge Base for relevant indicators
4. **Recommendations** → Returns formatted indicator recommendations with methods, costs, and rationale

## Knowledge Base Tools

The agent uses specialized search tools to query the CBA M&E Framework:

| Tool | Purpose |
|------|---------|
| `search_cba_indicators()` | General indicator search |
| `search_indicators_by_outcome()` | Find indicators aligned with project goals |
| `search_methods_by_budget()` | Filter by budget constraints |
| `search_location_specific_indicators()` | Region-specific recommendations |

## Component Roles

| Component | Role |
|-----------|------|
| **API Gateway** | Public HTTP endpoint that routes requests to Lambda |
| **Lambda** | Request router + orchestrator - calls AgentCore for chat, S3+Bedrock for uploads |
| **AgentCore** | Hosts the Strands agent with KB tools - does the actual "thinking" |
| **Knowledge Base** | Vector store with CBA indicators/methods (801 methods, 224 indicators) |
