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

---

## Bedrock AgentCore Infrastructure (CDK)

The production agent runs on **AWS Bedrock AgentCore**, deployed via CDK. Here's the complete infrastructure:

```mermaid
flowchart TB
    subgraph CDK["📦 CDK Deployment (cdk/bin/cdk.ts)"]
        direction TB
        DockerStack["DockerImageStack"]
        AgentCoreStack["AgentCoreStack"]
        DockerStack -->|"imageUri"| AgentCoreStack
    end

    subgraph ECR["Amazon ECR"]
        DockerImage["Docker Image<br/>(Python 3.12 + Strands Agent)"]
    end

    subgraph AgentCoreInfra["Bedrock AgentCore Infrastructure"]
        Runtime["AgentCore Runtime<br/>(cbaindicatoragent_Agent)"]
        Gateway["AgentCore Gateway<br/>(MCP Protocol)"]
        ACMemory["AgentCore Memory<br/>(30-day event expiry)"]
        
        subgraph Endpoints["Runtime Endpoints"]
            DEFAULT["DEFAULT"]
            PROD["PROD (v1)"]
            DEV["DEV (v1)"]
        end
    end

    subgraph Auth["🔐 Cognito Authentication"]
        UserPool["Cognito User Pool"]
        ResourceServer["Resource Server<br/>(basic scope)"]
        AppClient["App Client<br/>(client_credentials flow)"]
        Domain["Cognito Domain<br/>(cbaindicatoragent-{region})"]
    end

    subgraph MCPLayer["MCP Gateway Target"]
        MCPLambda["MCP Lambda<br/>(placeholder_tool)"]
    end

    subgraph IAM["IAM Roles"]
        RuntimeRole["Runtime Role<br/>(ECR, Logs, Bedrock, X-Ray)"]
        GatewayRole["Gateway Role<br/>(Lambda invoke)"]
    end

    %% CDK creates resources
    DockerStack -->|"builds"| DockerImage
    AgentCoreStack -->|"creates"| Runtime
    AgentCoreStack -->|"creates"| Gateway
    AgentCoreStack -->|"creates"| ACMemory
    AgentCoreStack -->|"creates"| UserPool
    AgentCoreStack -->|"creates"| MCPLambda

    %% Runtime configuration
    DockerImage -->|"containerUri"| Runtime
    RuntimeRole -->|"roleArn"| Runtime
    Runtime --> Endpoints

    %% Gateway configuration
    Gateway -->|"targetConfiguration"| MCPLambda
    GatewayRole -->|"roleArn"| Gateway
    UserPool -->|"JWT auth"| Gateway

    %% Auth flow
    UserPool --> ResourceServer
    ResourceServer --> AppClient
    AppClient --> Domain

    %% Environment variables passed to Runtime
    Runtime -.->|"GATEWAY_URL"| Gateway
    Runtime -.->|"MEMORY_ID"| ACMemory
    Runtime -.->|"COGNITO_*"| AppClient

    classDef cdk fill:#7B68EE,stroke:#483D8B,color:#fff
    classDef ecr fill:#FF9900,stroke:#232F3E,color:#232F3E
    classDef agentcore fill:#01A88D,stroke:#006644,color:#fff
    classDef auth fill:#DD344C,stroke:#8B0000,color:#fff
    classDef iam fill:#3F8624,stroke:#2E5A1C,color:#fff

    class DockerStack,AgentCoreStack cdk
    class DockerImage ecr
    class Runtime,Gateway,ACMemory,DEFAULT,PROD,DEV agentcore
    class UserPool,ResourceServer,AppClient,Domain auth
    class RuntimeRole,GatewayRole iam
```

### CDK Stack Components

| Resource | Type | Purpose |
|----------|------|---------|
| **DockerImageStack** | `ecr_assets.DockerImageAsset` | Builds and pushes agent Docker image to ECR |
| **AgentCore Runtime** | `bedrockagentcore.CfnRuntime` | Runs the containerized Strands agent |
| **AgentCore Gateway** | `bedrockagentcore.CfnGateway` | MCP protocol gateway for external tools |
| **AgentCore Memory** | `bedrockagentcore.CfnMemory` | Persistent memory with 30-day event expiry |
| **Cognito User Pool** | `cognito.UserPool` | JWT authentication for Gateway |
| **MCP Lambda** | `lambda.Function` | Placeholder tool for Gateway demonstration |

---

## End-to-End Data Flow

This diagram shows the complete request lifecycle from user input to response:

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 User
    participant NextJS as Next.js Frontend
    participant APIGW as API Gateway
    participant Lambda as Lambda Function
    participant AgentCore as AgentCore Runtime
    participant Strands as Strands Agent
    participant Bedrock as Bedrock (Claude)
    participant KB as Knowledge Base
    participant S3 as S3 Bucket

    Note over User,S3: === Chat Flow ===
    
    User->>NextJS: Enter message + project profile
    NextJS->>APIGW: POST /chat {message, session_id, profile}
    APIGW->>Lambda: Invoke lambda_handler()
    Lambda->>Lambda: Route to handle_chat()
    
    Lambda->>AgentCore: invoke_agent_runtime()<br/>ARN: cbaindicatoragent_Agent
    
    AgentCore->>Strands: Execute agent with prompt
    
    Note over Strands,KB: Agent Tool Loop
    
    Strands->>Strands: Parse user intent
    Strands->>Bedrock: LLM call (Claude Sonnet 4.5)
    Bedrock-->>Strands: Determine tools to call
    
    alt Profile Collection
        Strands->>Strands: set_project_location()
        Strands->>Strands: set_project_commodity()
        Strands->>Strands: set_project_budget()
        Strands->>Strands: set_project_outcomes()
    end
    
    alt Knowledge Base Search
        Strands->>KB: search_cba_indicators(query)
        KB-->>Strands: Indicator results (relevance scored)
        Strands->>KB: search_indicators_by_outcome(outcome)
        KB-->>Strands: Outcome-aligned indicators
        Strands->>KB: search_methods_by_budget(budget)
        KB-->>Strands: Budget-appropriate methods
    end
    
    Strands->>Bedrock: Generate final response
    Bedrock-->>Strands: Formatted recommendations
    
    Strands-->>AgentCore: Stream response chunks
    AgentCore-->>Lambda: SSE data events
    Lambda->>Lambda: Parse & clean response
    Lambda-->>APIGW: {response, session_id}
    APIGW-->>NextJS: JSON response
    NextJS-->>User: Display recommendations

    Note over User,S3: === Upload Flow ===
    
    User->>NextJS: Upload PDF file
    NextJS->>APIGW: POST /upload (FormData)
    APIGW->>Lambda: Invoke lambda_handler()
    Lambda->>Lambda: Route to handle_upload()
    Lambda->>S3: put_object() - store file
    S3-->>Lambda: s3://cba-indicator-uploads/...
    Lambda->>Bedrock: invoke_model() - extract profile
    Bedrock-->>Lambda: {location, commodity, budget}
    Lambda-->>APIGW: {found: {...}, missing: [...]}
    APIGW-->>NextJS: Extracted profile data
    NextJS-->>User: Pre-fill chat with profile
```

---

## AgentCore Container Architecture

The Strands agent runs inside a Docker container managed by AgentCore:

```mermaid
flowchart TB
    subgraph Container["🐳 Docker Container (Python 3.12)"]
        direction TB
        
        subgraph EntryPoint["Entry Point"]
            OTel["OpenTelemetry Instrument"]
            Main["src/main.py"]
            OTel --> Main
        end
        
        subgraph AgentSetup["Agent Configuration"]
            App["BedrockAgentCoreApp()"]
            SessionMgr["AgentCoreMemorySessionManager"]
            Model["BedrockModel<br/>(global.anthropic.claude-sonnet-4-5)"]
        end
        
        subgraph Tools["🔧 Agent Tools"]
            direction LR
            ProfileTools["Profile Tools<br/>set_project_*<br/>get_project_profile"]
            KBTools["KB Tools<br/>search_cba_indicators<br/>search_indicators_by_outcome<br/>search_methods_by_budget<br/>search_location_specific"]
            MCPTools["MCP Tools<br/>(via Gateway)"]
        end
        
        subgraph KBClient["Knowledge Base Client"]
            Boto3["boto3 bedrock-agent-runtime"]
            Retrieve["retrieve() API"]
        end
        
        Main --> App
        App --> SessionMgr
        App --> Model
        Main -->|"@app.entrypoint"| invoke["async invoke(payload, context)"]
        invoke --> Agent["Strands Agent"]
        Agent --> Tools
        KBTools --> KBClient
    end
    
    subgraph EnvVars["Environment Variables"]
        AWS_REGION["AWS_REGION"]
        GATEWAY_URL["GATEWAY_URL"]
        MEMORY_ID["MEMORY_ID"]
        COGNITO["COGNITO_CLIENT_ID<br/>COGNITO_CLIENT_SECRET<br/>COGNITO_TOKEN_URL<br/>COGNITO_SCOPE"]
        KB_ID["KNOWLEDGE_BASE_ID"]
    end
    
    subgraph External["External Services"]
        BedrockSvc["Amazon Bedrock"]
        KBSvc["Knowledge Base<br/>(ID: 0ZQBMXEKDI)"]
        MemorySvc["AgentCore Memory"]
        GatewaySvc["AgentCore Gateway"]
    end
    
    EnvVars -.-> Container
    KBClient -->|"retrieve()"| KBSvc
    Model -->|"invoke_model()"| BedrockSvc
    SessionMgr -->|"session state"| MemorySvc
    MCPTools -->|"MCP protocol"| GatewaySvc

    classDef container fill:#2496ED,stroke:#1D76B8,color:#fff
    classDef tools fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef external fill:#FF9900,stroke:#232F3E,color:#232F3E
    classDef env fill:#9C27B0,stroke:#6A1B9A,color:#fff

    class Container,EntryPoint,AgentSetup,KBClient container
    class ProfileTools,KBTools,MCPTools tools
    class BedrockSvc,KBSvc,MemorySvc,GatewaySvc external
    class AWS_REGION,GATEWAY_URL,MEMORY_ID,COGNITO,KB_ID env
```

### Container Details

| Component | File | Purpose |
|-----------|------|---------|
| **Dockerfile** | `agentcore-cba/cbaindicatoragent/Dockerfile` | Python 3.12 slim + uv + OpenTelemetry |
| **Entry Point** | `src/main.py` | BedrockAgentCoreApp with `@app.entrypoint` |
| **Model Loader** | `src/model/load.py` | Returns `BedrockModel` with global inference profile |
| **KB Tools** | `src/kb_tool.py` | Boto3 calls to `bedrock-agent-runtime.retrieve()` |
| **MCP Client** | `src/mcp_client/client.py` | Cognito auth + streamable HTTP to Gateway |

---

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

---

## Request Flow Code Details

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

---

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
| **AgentCore Runtime** | Hosts the containerized Strands agent |
| **AgentCore Gateway** | MCP protocol endpoint for external tools |
| **AgentCore Memory** | Persistent session/event storage (30-day TTL) |
| **Knowledge Base** | Vector store with CBA indicators/methods (801 methods, 224 indicators) |
| **Cognito** | JWT authentication for Gateway access |
