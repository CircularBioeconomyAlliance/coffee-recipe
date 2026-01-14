# CBA Indicator Selection Assistant - Architecture

This document describes the production architecture of the CBA (Circular Bioeconomy Alliance) Indicator Selection Assistant.

## System Overview

```mermaid
flowchart TB
    subgraph Users["👤 Users"]
        Web["Web Browser"]
    end

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

    subgraph AWS["AWS Services"]
        Bedrock["Amazon Bedrock<br/>(Claude Sonnet 4.5)"]
        KB["Bedrock Knowledge Base<br/>(801 methods, 224 indicators)"]
        S3["S3 Bucket<br/>(File Uploads)"]
        APIGateway["API Gateway"]
    end

    %% User flow
    Web --> ChatPage
    Web --> UploadPage

    %% Frontend to backend
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

    %% KB Search functions
    KBTool -.-> |"search_cba_indicators()"| KB
    KBTool -.-> |"search_indicators_by_outcome()"| KB
    KBTool -.-> |"search_methods_by_budget()"| KB
    KBTool -.-> |"search_location_specific_indicators()"| KB

    classDef aws fill:#FF9900,stroke:#232F3E,color:#232F3E
    classDef frontend fill:#61DAFB,stroke:#20232A,color:#20232A
    classDef python fill:#3776AB,stroke:#FFD43B,color:#fff

    class Bedrock,KB,S3,APIGateway aws
    class ChatPage,UploadPage,ResultsPage,ApiLib frontend
    class Handler,MainAgent,KBTool python
```

## Key Components

| Component | Purpose |
|-----------|---------|
| **`cba-frontend/`** | Next.js frontend with chat UI and file upload |
| **`lambda_function.py`** | Lambda handler routing `/chat` and `/upload` requests |
| **`agentcore-cba/`** | Bedrock AgentCore with Strands agent and KB tools |

---

## Bedrock AgentCore Infrastructure (CDK)

The agent runs on **AWS Bedrock AgentCore**, deployed via CDK:

```mermaid
flowchart TB
    subgraph CDK["📦 CDK Deployment"]
        DockerStack["DockerImageStack"]
        AgentCoreStack["AgentCoreStack"]
        DockerStack -->|"imageUri"| AgentCoreStack
    end

    subgraph ECR["Amazon ECR"]
        DockerImage["Docker Image<br/>(Python 3.12 + Strands)"]
    end

    subgraph AgentCoreInfra["Bedrock AgentCore"]
        Runtime["AgentCore Runtime<br/>(cbaindicatoragent_Agent)"]
        Gateway["AgentCore Gateway<br/>(MCP Protocol)"]
        ACMemory["AgentCore Memory<br/>(30-day expiry)"]
        
        subgraph Endpoints["Runtime Endpoints"]
            DEFAULT["DEFAULT"]
            PROD["PROD"]
            DEV["DEV"]
        end
    end

    subgraph Auth["🔐 Cognito"]
        UserPool["User Pool"]
        AppClient["App Client<br/>(client_credentials)"]
    end

    subgraph MCPLayer["MCP Gateway"]
        MCPLambda["MCP Lambda"]
    end

    %% CDK creates resources
    DockerStack -->|"builds"| DockerImage
    AgentCoreStack -->|"creates"| Runtime
    AgentCoreStack -->|"creates"| Gateway
    AgentCoreStack -->|"creates"| ACMemory
    AgentCoreStack -->|"creates"| UserPool

    %% Runtime config
    DockerImage -->|"containerUri"| Runtime
    Runtime --> Endpoints
    Gateway -->|"target"| MCPLambda
    UserPool -->|"JWT auth"| Gateway

    classDef cdk fill:#7B68EE,stroke:#483D8B,color:#fff
    classDef ecr fill:#FF9900,stroke:#232F3E,color:#232F3E
    classDef agentcore fill:#01A88D,stroke:#006644,color:#fff
    classDef auth fill:#DD344C,stroke:#8B0000,color:#fff

    class DockerStack,AgentCoreStack cdk
    class DockerImage ecr
    class Runtime,Gateway,ACMemory,DEFAULT,PROD,DEV agentcore
    class UserPool,AppClient auth
```

### Infrastructure Resources

| Resource | Type | Purpose |
|----------|------|---------|
| **DockerImageStack** | ECR Asset | Builds agent Docker image |
| **AgentCore Runtime** | `CfnRuntime` | Runs containerized Strands agent |
| **AgentCore Gateway** | `CfnGateway` | MCP protocol for external tools |
| **AgentCore Memory** | `CfnMemory` | Session storage (30-day TTL) |
| **Cognito** | User Pool | JWT authentication for Gateway |

---

## End-to-End Data Flow

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 User
    participant NextJS as Next.js
    participant APIGW as API Gateway
    participant Lambda as Lambda
    participant AgentCore as AgentCore
    participant Bedrock as Claude (Bedrock)
    participant KB as Knowledge Base
    participant S3 as S3

    Note over User,S3: Chat Flow
    
    User->>NextJS: Enter message
    NextJS->>APIGW: POST /chat
    APIGW->>Lambda: Invoke
    Lambda->>AgentCore: invoke_agent_runtime()
    
    AgentCore->>Bedrock: LLM call
    Bedrock-->>AgentCore: Determine tools
    
    AgentCore->>KB: search_cba_indicators()
    KB-->>AgentCore: Indicator results
    
    AgentCore->>Bedrock: Generate response
    Bedrock-->>AgentCore: Recommendations
    
    AgentCore-->>Lambda: Stream response
    Lambda-->>APIGW: JSON
    APIGW-->>NextJS: Response
    NextJS-->>User: Display results

    Note over User,S3: Upload Flow
    
    User->>NextJS: Upload PDF
    NextJS->>APIGW: POST /upload
    APIGW->>Lambda: Invoke
    Lambda->>S3: Store file
    Lambda->>Bedrock: Extract profile
    Bedrock-->>Lambda: {location, commodity, budget}
    Lambda-->>NextJS: Profile data
    NextJS-->>User: Pre-fill chat
```

---

## Request Flow Details

### 1. Frontend → API Gateway

```typescript
// cba-frontend/lib/api.ts
const API_URL = "https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod";

await fetch(`${API_URL}/chat`, {
  method: "POST",
  body: JSON.stringify({ message, session_id, profile })
});
```

### 2. Lambda Routes Requests

```python
# lambda_function.py
def lambda_handler(event, context):
    if '/chat' in path:
        return handle_chat(event)      # → AgentCore
    elif '/upload' in path:
        return handle_upload(event)    # → S3 + Bedrock
```

### 3. AgentCore Invocation

```python
# handle_chat()
response = agentcore.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:...:runtime/cbaindicatoragent_Agent-...',
    runtimeSessionId=session_id,
    payload=json.dumps({"prompt": message}).encode()
)
```

---

## AgentCore Container

```mermaid
flowchart TB
    subgraph Container["🐳 Docker Container"]
        Main["src/main.py"]
        Model["BedrockModel<br/>(Claude Sonnet 4.5)"]
        
        subgraph Tools["Agent Tools"]
            ProfileTools["set_project_*<br/>get_project_profile"]
            KBTools["search_cba_indicators<br/>search_by_outcome<br/>search_by_budget<br/>search_by_location"]
        end
        
        subgraph KBClient["KB Client"]
            Boto3["bedrock-agent-runtime"]
        end
        
        Main --> Model
        Main --> Tools
        KBTools --> KBClient
    end
    
    subgraph External["AWS Services"]
        BedrockSvc["Amazon Bedrock"]
        KBSvc["Knowledge Base<br/>(ID: 0ZQBMXEKDI)"]
    end
    
    KBClient -->|"retrieve()"| KBSvc
    Model -->|"invoke_model()"| BedrockSvc

    classDef container fill:#2496ED,stroke:#1D76B8,color:#fff
    classDef tools fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef external fill:#FF9900,stroke:#232F3E,color:#232F3E

    class Container,Main,Model,KBClient container
    class ProfileTools,KBTools tools
    class BedrockSvc,KBSvc external
```

---

## Knowledge Base Tools

| Tool | Purpose |
|------|---------|
| `search_cba_indicators(query)` | General indicator search |
| `search_indicators_by_outcome(outcome)` | Find indicators for project goals |
| `search_methods_by_budget(budget)` | Filter by budget constraints |
| `search_location_specific_indicators(location)` | Region-specific recommendations |

---

## Component Summary

| Component | Role |
|-----------|------|
| **API Gateway** | Public HTTP endpoint |
| **Lambda** | Request router → AgentCore for chat, S3+Bedrock for uploads |
| **AgentCore Runtime** | Containerized Strands agent |
| **AgentCore Gateway** | MCP protocol for external tools |
| **AgentCore Memory** | Session storage (30-day TTL) |
| **Knowledge Base** | 801 methods, 224 indicators |
| **Cognito** | JWT authentication |
