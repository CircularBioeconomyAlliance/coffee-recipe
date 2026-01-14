# CBA Indicator Assistant - Presenter Guide

> **Use this guide to present the "How It Works" slide**

---

## 🎤 Talking Points (30-45 seconds)

### 1. Two Entry Points (10 sec)
"Users can start two ways: **chat directly** with the AI, or **upload a project PDF**. The upload option extracts information automatically so the AI only asks for what's missing."

### 2. The Flow (15 sec)
"Either way, we collect four things: **location, commodity, budget, and outcomes**. The agent then searches our **Knowledge Base of 800+ methods** and returns tailored indicator recommendations."

### 3. Tech Stack (10 sec)
"It's built on **AWS Bedrock** with Claude Sonnet, using **AgentCore** for the agent runtime and a **Next.js frontend**. Fully serverless."

---

## 📊 Architecture Diagram

```
                            ┌─────────────────────────────────────────────────────────┐
                            │                      AWS CLOUD                          │
                            │                                                         │
   ┌──────────┐             │   ┌───────────┐    ┌─────────────┐    ┌─────────────┐  │
   │  Next.js │  ─── /chat ───► │   API     │───►│   Lambda    │───►│  AgentCore  │  │
   │ Frontend │             │   │  Gateway  │    │             │    │  (Strands)  │  │
   └──────────┘             │   └───────────┘    └──────┬──────┘    └──────┬──────┘  │
        │                   │                          │                   │         │
        │                   │                          │                   │         │
        │ /upload           │                          ▼                   ▼         │
        │                   │                    ┌──────────┐       ┌─────────────┐  │
        └───────────────────┼──────────────────►│    S3    │       │  Knowledge  │  │
                            │                    │  Bucket  │       │    Base     │  │
                            │                    └──────────┘       │(801 methods)│  │
                            │                                       └─────────────┘  │
                            │                          │                   ▲         │
                            │                          ▼                   │         │
                            │                    ┌──────────┐              │         │
                            │                    │  Claude  │──────────────┘         │
                            │                    │ (Bedrock)│                         │
                            │                    └──────────┘                         │
                            └─────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flows

### Flow A: Chat
```
User types message
       │
       ▼
POST /chat → Lambda → AgentCore → Claude + KB Search → Response
```

### Flow B: Document Upload
```
User uploads PDF
       │
       ▼
POST /upload → Lambda → S3 (store) → Claude (extract profile) → Return {location, commodity, budget}
       │
       ▼
Frontend pre-fills chat → Agent asks for missing info (e.g., outcomes) → KB Search → Response
```

---

## 🧩 Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js | Chat UI, file upload |
| **API** | API Gateway | HTTP routing |
| **Compute** | Lambda | Request handling |
| **Agent** | Bedrock AgentCore + Strands | Conversation + tool orchestration |
| **LLM** | Claude Sonnet 4.5 | Reasoning, extraction, responses |
| **Data** | Bedrock Knowledge Base | 801 methods, 224 indicators |
| **Storage** | S3 | Uploaded PDFs |
| **Auth** | Cognito | Gateway authentication |

---

## 🔧 What the Agent Collects

| Field | Required | Source |
|-------|----------|--------|
| 📍 Location | Yes | PDF or chat |
| 🌾 Commodity | Yes | PDF or chat |
| 💰 Budget | Yes | PDF or chat |
| 🎯 Outcomes | Yes | Usually chat (rarely in PDFs) |
| ⚙️ Technical Capacity | Optional | Chat |

---

## 🛠️ Agent Tools

| Tool | What It Does |
|------|--------------|
| `search_cba_indicators(query)` | General KB search |
| `search_indicators_by_outcome(outcome)` | Find indicators for goals |
| `search_methods_by_budget(budget)` | Filter by cost |
| `search_location_specific_indicators(location)` | Regional relevance |
| `set_project_*` | Store profile fields |

---

## ❓ If Asked...

**"How does the PDF extraction work?"**
> Document is uploaded to S3, then Claude extracts location, commodity, and budget. The agent identifies what's missing and asks follow-up questions.

**"What's in the Knowledge Base?"**
> 801 measurement methods and 224 indicators from the CBA M&E Framework — curated by sustainability experts.

**"Is it serverless?"**
> Yes — Lambda, AgentCore, and Bedrock. Pay only for what you use.
