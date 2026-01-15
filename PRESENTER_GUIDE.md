# CBA Indicator Assistant - Presenter Guide

> **Use this guide to present the "How It Works" slide**

---

## Notes:
## Talking points (45 seconds)

* **Two ways in**

  * Users either start by chatting, or they upload a project PDF.
  * Uploads go to S3 and we extract the basics up front, so we only ask what’s missing. 

* **Project profile**

  * We capture location, commodity, budget, and intended outcomes, plus technical capacity if needed. 

* **Decision flow**

  * Step one: find indicators that are genuinely relevant to the project.
  * Step two: for those indicators, return the measurement methods that match requirements and constraints, especially cost and practicality. 

* **What the user sees**

  * Results stream back into the chat as they’re generated, so it feels immediate. 

* **Tech close**

  * Front end: static Next.js hosted on **S3 + CloudFront**.
  * Back end: API Gateway + Lambda.
  * Agent: **Strands running on Bedrock AgentCore** with Claude Sonnet and the Knowledge Base. 


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
| **Frontend** | Next.js (Static Export) | Chat UI, file upload |
| **API** | API Gateway (HTTP API) | HTTP routing, JWT validation |
| **Compute** | Lambda | Request handling |
| **Agent** | Bedrock AgentCore + Strands | Conversation + tool orchestration |
| **LLM** | Claude Sonnet 4 | Reasoning, extraction, responses |
| **Data** | Bedrock Knowledge Base | 801 methods, 224 indicators |
| **Storage** | S3 | Uploaded PDFs, static frontend |
| **Auth** | Cognito | User pools, JWT tokens |
| **CDN** | CloudFront | Edge caching, HTTPS |

---

## 🌐 Frontend Deployment

**Static Export + Client-Side API Calls**

```
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND DEPLOYMENT                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Next.js Build (static)                                     │
│         │                                                    │
│         ▼                                                    │
│   ┌───────────┐    ┌────────────┐    ┌──────────┐           │
│   │   HTML    │───►│ CloudFront │◄───│  Browser │           │
│   │  JS/CSS   │    │   (CDN)    │    │          │           │
│   │  (in S3)  │    └────────────┘    └────┬─────┘           │
│   └───────────┘                           │                  │
│                                           │ API calls        │
│                                           ▼                  │
│                                    ┌─────────────┐           │
│                                    │ API Gateway │           │
│                                    │  (Lambda)   │           │
│                                    └─────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| Aspect | Details |
|--------|---------|
| **Build Type** | Static export (`next build && next export`) |
| **Hosting** | S3 bucket + CloudFront distribution |
| **Rendering** | Client-side React (no SSR needed) |
| **API Calls** | Browser → API Gateway → Lambda (CORS enabled) |
| **State** | React state + URL params (no server sessions) |
| **Cost** | Near-zero (S3 storage + CloudFront requests) |

> **Why Static?** No server = no cold starts, global CDN caching, simpler deployment, and lower cost. All dynamic behavior happens via API calls.

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

## ⭐ Architecture Highlights

| Feature | Why It Matters |
|---------|----------------|
| **Streaming Responses** | Chat responses stream in real-time (not waiting for full completion) — feels responsive |
| **RAG Pattern** | Knowledge Base uses Retrieval Augmented Generation — Claude searches first, then reasons |
| **Stateless Lambda** | No session state in Lambda — all context passed per request or stored in AgentCore Memory |
| **AgentCore Memory** | Short-term (conversation) + Long-term (user preferences) memory persists across sessions |
| **Tool Orchestration** | AgentCore automatically decides which tools to call — no manual routing logic |
| **Containerized Agent** | Agent code runs in a managed container — deploy once, scale automatically |
| **JWT Auth Flow** | Cognito issues tokens → API Gateway validates → Lambda trusts claims |

---

## ❓ If Asked...

**"How does the PDF extraction work?"**
> Document is uploaded to S3, then Claude extracts location, commodity, and budget. The agent identifies what's missing and asks follow-up questions.

**"What's in the Knowledge Base?"**
> 801 measurement methods and 224 indicators from the CBA M&E Framework — curated by sustainability experts.

**"Is it serverless?"**
> Yes — Lambda, AgentCore, and Bedrock. Pay only for what you use.

**"Is the frontend static or dynamic?"**
> Static. Next.js exports HTML/JS/CSS to S3, served via CloudFront. All dynamic behavior happens through API calls to Lambda.

**"How does streaming work?"**
> AgentCore streams response chunks as they're generated. The frontend reads them via Server-Sent Events, so users see text appear progressively.

**"Does it remember previous conversations?"**
> Yes — AgentCore Memory stores short-term context (current session) and long-term preferences (returning users). Users can pick up where they left off.

**"What happens if the agent can't find indicators?"**
> The agent asks clarifying questions, broadens the search, or explains why certain outcomes may have limited measurement options in the Knowledge Base.

**"How do you handle concurrent users?"**
> Each request is independent — Lambda scales horizontally, AgentCore manages agent instances, and session IDs keep conversations separate.
