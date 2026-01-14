# AgentCore Memory Architecture

This document explains how memory is implemented in the CBA Indicator Assistant agent, what data is stored where, and how it improves the agent's capabilities.

## Overview

The agent uses **Amazon Bedrock AgentCore Memory** to maintain context across conversations. This enables the agent to:

- Remember what was discussed within a session (Short-Term Memory)
- Learn user preferences over time (Long-Term Memory)
- Recall project facts without users repeating them
- Provide personalized, contextual responses

## Memory Components

### Session Identifiers

| Identifier | Purpose | Scope |
|------------|---------|-------|
| `session_id` | Identifies a single conversation thread | One conversation |
| `actor_id` | Identifies a user across sessions | All conversations for a user |
| `runtime_session_id` | AgentCore Runtime microVM isolation | Infrastructure-level |

### Memory ID

```
CBA_Indicator_Assistant_Memory-BhKqkC8Yqa
```

This is the unique identifier for our memory resource in AWS Bedrock AgentCore.

---

## Short-Term Memory (STM)

**Always active** - Stores the conversation history within a single session.

### What's Stored

| Data Type | Example | Retention |
|-----------|---------|-----------|
| User messages | "I need indicators for a cotton project in Chad" | Session duration |
| Agent responses | "Here are 5 recommended indicators..." | Session duration |
| Tool invocations | `memory.retrieve(query="soil health")` | Session duration |
| Tool results | Retrieved 10 indicators from Knowledge Base | Session duration |

### Namespace

```
/sessions/{sessionId}
```

### How It Helps

- Agent maintains conversation flow without losing context
- Multi-turn conversations work naturally
- User doesn't need to repeat information within a session

### Technical Details

STM is automatically managed by the `AgentCoreMemorySessionManager`. Each message exchange is stored as an event:

```python
# Automatically stored by the session manager
{
    "eventType": "USER_MESSAGE",
    "content": "What indicators should I use for soil health?",
    "timestamp": "2026-01-14T13:45:00Z",
    "sessionId": "abc-123",
    "actorId": "user-456"
}
```

---

## Long-Term Memory (LTM) Strategies

We configured three LTM strategies that extract and store information across sessions.

### 1. Summary Memory Strategy

**Purpose:** Automatically generates conversation summaries at session end.

### What's Stored

| Data Type | Example |
|-----------|---------|
| Session summary | "User asked about cotton farming indicators for Chad. Has low budget and basic technical capacity. Recommended soil health, yield, and water efficiency indicators." |
| Key decisions | "Selected indicators: IND-001, IND-045, IND-078" |
| Outcomes | "User exported results to CSV" |

### Namespace

```
/summaries/{actorId}/{sessionId}
```

### How It Helps

- When user returns for a new session, agent can recall previous conversations
- Provides continuity across separate chat sessions
- Helps agent understand user's history with the system

### Configuration

```python
"summaryMemoryStrategy": {
    "name": "SessionSummarizer",
    "namespaces": ["/summaries/{actorId}/{sessionId}"]
}
```

---

### 2. User Preference Strategy

**Purpose:** Extracts and stores user preferences that persist across all sessions.

### What's Stored

| Preference Type | Example Values |
|-----------------|----------------|
| Budget level | "User prefers low-cost measurement methods" |
| Technical capacity | "User has basic technical capacity, needs simple methods" |
| Output format | "User prefers results in table format" |
| Communication style | "User likes concise, actionable responses" |
| Domain focus | "User focuses on soil health and carbon sequestration" |

### Namespace

```
/preferences/{actorId}
```

### How It Helps

- Agent automatically tailors responses to user preferences
- No need to re-specify constraints in every session
- Personalized experience improves over time

### Configuration

```python
"userPreferenceMemoryStrategy": {
    "name": "PreferenceLearner", 
    "namespaces": ["/preferences/{actorId}"]
}
```

---

### 3. Semantic Memory Strategy

**Purpose:** Extracts facts and entities mentioned in conversations.

### What's Stored

| Fact Type | Example |
|-----------|---------|
| Project location | "User's project is in Chad, Sahel region" |
| Crop/livestock types | "User is growing cotton and sorghum" |
| Organizations | "User works with FAO and local NGOs" |
| Geographic coordinates | "Project site: 15.0°N, 19.0°E" |
| Project constraints | "Limited access to laboratory equipment" |
| Stakeholders | "Working with smallholder farmers" |

### Namespace

```
/facts/{actorId}
```

### How It Helps

- Agent knows project context without user repeating it
- Can make connections between related facts
- Enables proactive suggestions based on known context

### Configuration

```python
"semanticMemoryStrategy": {
    "name": "FactExtractor",
    "namespaces": ["/facts/{actorId}"]
}
```

---

## Retrieval Configuration

When the agent processes a request, it retrieves relevant memories using this configuration:

```python
retrieval_config={
    # User preferences - high relevance threshold
    "/preferences/{actorId}": RetrievalConfig(
        top_k=5,           # Retrieve top 5 preferences
        relevance_score=0.7  # 70% similarity threshold
    ),
    
    # Project facts - more permissive threshold
    "/facts/{actorId}": RetrievalConfig(
        top_k=10,          # Retrieve top 10 facts
        relevance_score=0.5  # 50% similarity threshold
    ),
    
    # Session summaries - moderate threshold
    "/summaries/{actorId}/{sessionId}": RetrievalConfig(
        top_k=5,           # Retrieve top 5 summaries
        relevance_score=0.6  # 60% similarity threshold
    ),
}
```

### Parameter Explanation

| Parameter | Description |
|-----------|-------------|
| `top_k` | Maximum number of memory items to retrieve |
| `relevance_score` | Minimum similarity threshold (0.0 - 1.0) for retrieval |

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER REQUEST                                  │
│  "What indicators should I use for my cotton project?"              │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 AgentCoreMemorySessionManager                        │
│                                                                      │
│  RETRIEVAL PHASE (before agent processes request):                  │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 1. STM: Load conversation history for this session             │ │
│  │    → "Earlier user mentioned Chad location"                    │ │
│  │                                                                │ │
│  │ 2. /preferences/{actorId}: Retrieve user preferences           │ │
│  │    → "Prefers low-budget methods"                              │ │
│  │    → "Has basic technical capacity"                            │ │
│  │                                                                │ │
│  │ 3. /facts/{actorId}: Retrieve known facts                      │ │
│  │    → "Project in Chad, Sahel region"                           │ │
│  │    → "Growing cotton"                                          │ │
│  │                                                                │ │
│  │ 4. /summaries/{actorId}/*: Retrieve past session summaries     │ │
│  │    → "Previously discussed soil health indicators"             │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         STRANDS AGENT                                │
│                                                                      │
│  Agent now has full context:                                        │
│  • Current request + conversation history                           │
│  • User's known preferences                                         │
│  • Project facts                                                    │
│  • Previous session context                                         │
│                                                                      │
│  → Generates contextual, personalized response                      │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT RESPONSE                                │
│  "Based on your cotton project in Chad with low budget and basic    │
│   capacity, here are 5 recommended indicators..."                   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 AgentCoreMemorySessionManager                        │
│                                                                      │
│  STORAGE PHASE (after agent responds):                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 1. STM: Store this exchange in session history                 │ │
│  │                                                                │ │
│  │ 2. LTM Strategies automatically extract and store:             │ │
│  │    • New facts mentioned                                       │ │
│  │    • Preference signals                                        │ │
│  │    • (At session end) Conversation summary                     │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Code Implementation

### Configuration (`src/config.py`)

```python
# AgentCore Memory ID - created via scripts/setup_memory.py
AGENTCORE_MEMORY_ID = os.environ.get(
    "AGENTCORE_MEMORY_ID", 
    "CBA_Indicator_Assistant_Memory-BhKqkC8Yqa"
)
```

### Session Manager Setup (`src/bedrock_agent.py`)

```python
from bedrock_agentcore.memory.integrations.strands.config import (
    AgentCoreMemoryConfig,
    RetrievalConfig,
)
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)

# Configure memory with retrieval settings
config = AgentCoreMemoryConfig(
    memory_id=AGENTCORE_MEMORY_ID,
    session_id=session_id,
    actor_id=actor_id,
    retrieval_config={
        "/preferences/{actorId}": RetrievalConfig(top_k=5, relevance_score=0.7),
        "/facts/{actorId}": RetrievalConfig(top_k=10, relevance_score=0.5),
        "/summaries/{actorId}/{sessionId}": RetrievalConfig(top_k=5, relevance_score=0.6),
    },
)

# Create session manager
session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=config,
    region_name=AWS_REGION
)

# Create agent with session manager
agent = Agent(
    model=bedrock_model,
    system_prompt=SYSTEM_PROMPT,
    session_manager=session_manager,
    tools=[memory, use_llm, http_request, file_write, current_time],
)
```

### Memory Resource Creation (`scripts/setup_memory.py`)

```python
strategies = {
    "summaryMemoryStrategy": {
        "name": "SessionSummarizer",
        "namespaces": ["/summaries/{actorId}/{sessionId}"]
    },
    "userPreferenceMemoryStrategy": {
        "name": "PreferenceLearner",
        "namespaces": ["/preferences/{actorId}"]
    },
    "semanticMemoryStrategy": {
        "name": "FactExtractor",
        "namespaces": ["/facts/{actorId}"]
    }
}

memory_client.create_memory_and_wait(
    name="CBA_Indicator_Assistant_Memory",
    strategies=strategies
)
```

---

## AWS Resources

### Memory Resource

| Property | Value |
|----------|-------|
| Memory ID | `CBA_Indicator_Assistant_Memory-BhKqkC8Yqa` |
| Region | `us-west-2` |
| ARN | `arn:aws:bedrock-agentcore:us-west-2:687995992314:memory/CBA_Indicator_Assistant_Memory-BhKqkC8Yqa` |

### IAM Permissions

The execution role requires these permissions for memory access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:ListEvents",
                "bedrock-agentcore:CreateEvent",
                "bedrock-agentcore:GetMemory",
                "bedrock-agentcore:InvokeMemory"
            ],
            "Resource": "arn:aws:bedrock-agentcore:us-west-2:687995992314:memory/CBA_Indicator_Assistant_Memory-BhKqkC8Yqa"
        }
    ]
}
```

---

## Observability

### CloudWatch Logs

Memory operations are logged to:
```
/aws/vendedlogs/bedrock-agentcore/memory/APPLICATION_LOGS/CBA_Indicator_Assistant_Memory-BhKqkC8Yqa
```

### Monitoring Dashboard

View memory metrics in the GenAI Observability Dashboard:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core
```

---

## Best Practices

1. **Use consistent `actor_id`** - Always pass the same `actor_id` for the same user to ensure LTM works correctly across sessions.

2. **Generate unique `session_id`** - Each new conversation should have a unique `session_id`.

3. **Tune retrieval thresholds** - Adjust `relevance_score` based on your use case:
   - Higher (0.7+): More precise, fewer but more relevant results
   - Lower (0.5): More permissive, more results but potentially less relevant

4. **Monitor memory usage** - LTM strategies incur additional charges. Monitor usage in AWS Console.

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `AccessDeniedException` on ListEvents | Missing IAM permissions | Add memory permissions to execution role |
| Memory not persisting | Different `actor_id` each session | Use consistent user identifier |
| Slow responses | Large memory retrieval | Reduce `top_k` or increase `relevance_score` |

### Checking Memory Contents

Use the AWS CLI to inspect stored memories:

```bash
aws bedrock-agentcore list-events \
  --memory-id CBA_Indicator_Assistant_Memory-BhKqkC8Yqa \
  --namespace "/preferences/user-123" \
  --region us-west-2
```
