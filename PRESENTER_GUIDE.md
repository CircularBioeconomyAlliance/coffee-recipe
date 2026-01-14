# CBA Indicator Assistant - 45 Second Pitch

> **One-liner:** An AI assistant that helps sustainability projects pick the right monitoring indicators from a library of 800+ methods.

---

## 🎯 The Problem (10 sec)

"Circular bioeconomy projects need to track their impact, but choosing from **800+ measurement methods** is overwhelming. Projects often pick wrong indicators, wasting time and budget."

---

## 💡 The Solution (15 sec)

"We built an **AI chatbot** that asks about your project — location, crop, budget, goals — then searches our knowledge base to recommend the **perfect indicators** for your specific situation."

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   👤 User   │ ──► │  🤖 AI Chat │ ──► │ 📚 Search   │ ──► │ ✅ Results  │
│  "I grow    │     │  Asks about │     │  801 methods│     │  Top 5      │
│   coffee    │     │  location,  │     │  224 indica-│     │  indicators │
│   in Brazil"│     │  budget...  │     │  tors in KB │     │  for YOU    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

---

## 🔧 How It Works (15 sec)

| Step | What Happens |
|------|-------------|
| **1. Chat** | User describes their project in plain English |
| **2. Profile** | AI collects: location, commodity, budget, outcomes |
| **3. Search** | Queries AWS Bedrock Knowledge Base with 800+ methods |
| **4. Recommend** | Returns tailored indicators with methods & costs |

---

## ☁️ Tech Stack (5 sec)

- **Frontend:** Next.js
- **AI:** Claude Sonnet 4.5 via AWS Bedrock
- **Knowledge Base:** 801 methods, 224 indicators (CBA M&E Framework)
- **Infrastructure:** Bedrock AgentCore + Lambda + API Gateway

---

## 🎬 Demo Script

> **Say this while showing the chat interface:**

1. "Here's a coffee farmer in Brazil with a $10K budget"
2. "The AI asks what they want to measure — let's say 'soil health'"
3. "It searches our knowledge base and recommends 5 specific indicators"
4. "Each recommendation includes the method, cost, and why it fits their project"

---

## 📊 Architecture

```
   USER                    AWS CLOUD                     DATA
    │                         │                           │
    ▼                         ▼                           ▼
┌────────┐              ┌──────────┐              ┌────────────┐
│ Next.js│    ──────►   │  Lambda  │    ──────►   │ Knowledge  │
│Frontend│              │    +     │              │    Base    │
│        │   ◄──────    │AgentCore │   ◄──────    │(801 methods)│
└────────┘              └──────────┘              └────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │  Claude  │
                        │ (Bedrock)│
                        └──────────┘
```

---

## 🏆 Key Benefits

| For Users | For CBA |
|-----------|---------|
| ✅ No expertise needed | ✅ Scalable advice |
| ✅ Budget-aware recommendations | ✅ Consistent methodology |
| ✅ Location-specific indicators | ✅ Knowledge base grows over time |

---

## 💬 Elevator Pitch (Copy-Paste)

> "We built an AI assistant for the Circular Bioeconomy Alliance that helps sustainability projects choose the right monitoring indicators. Instead of manually searching through 800 measurement methods, users just chat with an AI about their project — where it is, what they're growing, their budget — and get personalized recommendations in seconds. It's powered by AWS Bedrock and our curated knowledge base of CBA indicators."

---

## ❓ Anticipated Questions

**Q: Where does the data come from?**
> A: The CBA M&E Framework — a curated library of 801 methods and 224 indicators developed by sustainability experts.

**Q: How accurate is it?**
> A: The AI only recommends indicators from our verified knowledge base. It never makes things up.

**Q: Can it handle different crops/regions?**
> A: Yes! It's designed for global use — coffee in Brazil, cotton in Chad, etc.

**Q: What's the cost?**
> A: Runs on AWS serverless (Lambda + Bedrock), so you only pay for what you use.
