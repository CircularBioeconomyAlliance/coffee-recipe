# CBA Indicator Selection Assistant - Code Review Report

## Executive Summary

The CBA Indicator Selection Assistant is an AI-powered tool for helping Circular Bioeconomy Alliance users find monitoring and evaluation indicators for sustainable agriculture projects. This review focuses on the **production stack**: the Next.js frontend, AWS Lambda backend, and Bedrock AgentCore agent.

> **Note:** The Streamlit app (`src/app.py`) and CLI agent (`src/agent.py`) are legacy/development components and are not covered in this review. The Next.js frontend in `cba-frontend/` is the only functional UI for production.

**Overall Assessment:** The production architecture is well-designed. Most critical issues from the original review have been fixed:
- ✅ Security vulnerabilities addressed (environment variables, input validation, proper error handling)
- ✅ Frontend now fetches real data from API with session tracking
- ✅ PDF upload extracts actual content for analysis
- ✅ Clear "DEMO DATA" warnings when using fallback data
- ⚠️ Remaining: In-memory recommendations store (use DynamoDB for production)

---

## Part 1: What Works Well

### 1.1 AgentCore Agent Implementation

The production agent in [agentcore-cba/cbaindicatoragent/src/main.py](agentcore-cba/cbaindicatoragent/src/main.py) is well-structured:

**What works:**

- Clean integration with Bedrock AgentCore framework
- Session-aware design with `session_id` from context
- Memory integration via `AgentCoreMemorySessionManager`
- Async streaming response with `stream_async()`
- Proper tool registration for profile management and KB search

### 1.2 Knowledge Base Tools

The [agentcore-cba/cbaindicatoragent/src/kb_tool.py](agentcore-cba/cbaindicatoragent/src/kb_tool.py) provides well-designed search tools:

```python
@tool
def search_cba_indicators(query: str, max_results: int = 10) -> str:
    """
    Search the CBA M&E Framework Knowledge Base for relevant indicators and methods.
    """
```

**What works:**

- Four specialized search tools for different query types:
  - `search_cba_indicators()` - General indicator search
  - `search_indicators_by_outcome()` - Outcome-aligned indicators
  - `search_methods_by_budget()` - Budget-appropriate methods
  - `search_location_specific_indicators()` - Region-specific recommendations
- Proper use of the `@tool` decorator
- Formatted output with relevance scores
- Error handling with user-friendly messages

### 1.3 Profile Management Tools

The AgentCore agent has tools for tracking project profile state:

```python
@tool
def set_project_location(location: str) -> str:
    """Set the project location/region"""
    project_profile["location"] = location
    return f"Location set to: {location}"

@tool
def get_project_profile() -> dict:
    """Get the current project profile"""
    return project_profile
```

**What works:**

- Clean tool interface for the agent to store user-provided information
- Supports all required fields: location, commodity, budget, outcomes, capacity

### 1.4 Lambda Router Structure

The [lambda_function.py](lambda_function.py) has clean request routing:

```python
def lambda_handler(event, context):
    path = event.get('rawPath', event.get('path', ''))
    method = event.get('requestContext', {}).get('http', {}).get('method', 'POST')
    
    if method == 'OPTIONS':
        return cors_response()
    
    if '/chat' in path:
        return handle_chat(event)
    elif '/upload' in path:
        return handle_upload(event)
    elif '/recommendations' in path:
        return handle_recommendations(event)
    else:
        return {
            'statusCode': 404,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Not found'})
        }
```

**What works:**

- Clean separation of chat, upload, and recommendations handlers
- CORS headers + preflight handling properly configured
- Handles both `/chat` and `/prod/chat` paths
- Session ID generation for new conversations
- Streaming response parsing from AgentCore

### 1.5 Next.js Frontend Design

The frontend in [cba-frontend/](cba-frontend/) has excellent UI/UX:

**What works:**

- Beautiful CBA-branded dark theme (#031f35 navy, #FBAD17 gold)
- Framer Motion animations for smooth transitions
- Responsive grid layouts
- Clear user flow: Home → Upload/Chat → Results → Compare
- Profile sidebar showing collected information
- Loading states with spinner animations
- Proper Suspense boundaries for client components

### 1.6 Chat Page Core Functionality

The [cba-frontend/app/chat/page.tsx](cba-frontend/app/chat/page.tsx) chat flow works:

**What works:**

- Real-time chat with the AgentCore backend via API
- Message history display with user/assistant styling
- Loading state during API calls
- URL parameter support for pre-filling from upload page
- Keyboard handling (Enter to send)

### 1.7 Upload Page Flow

The [cba-frontend/app/upload/page.tsx](cba-frontend/app/upload/page.tsx) file upload works:

**What works:**

- Drag-and-drop file upload with visual feedback
- File type validation (PDF only)
- File size display
- Analysis results display (found/missing information)
- Navigation to chat with extracted parameters

### 1.8 API Client

The [cba-frontend/lib/api.ts](cba-frontend/lib/api.ts) is clean and simple:

```typescript
export const api = {
  async chat(message: string, sessionId?: string, profile?: any) {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId, profile }),
    });
    if (!res.ok) throw new Error("Chat failed");
    return res.json();
  },

  async uploadFile(file: File) {
    const buffer = await file.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    const base64 = btoa(binary);

    const res = await fetch(`${API_URL}/upload`, {
      method: "POST",
      headers: { "Content-Type": "application/octet-stream" },
      body: base64,
    });
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  },

  async getRecommendations(sessionId: string) {
    const res = await fetch(`${API_URL}/recommendations?session_id=${encodeURIComponent(sessionId)}`);
    if (!res.ok) throw new Error("Failed to fetch recommendations");
    return res.json();
  },
};
```

**What works:**

- Environment variable support for API URL
- Clean async/await pattern
- Error throwing for non-OK responses

---

## Part 2: What Was Fixed

The following issues from the original code review have been addressed:

### 2.1 ✅ Frontend Results Page - Now Connected to Backend

**Status:** FIXED

The results page now:
- Fetches recommendations from the `/recommendations` API endpoint using session_id
- Falls back to example data only when no session or API fails
- Shows prominent "DEMO DATA" warning banner when using fallback data
- Each card shows "EXAMPLE" ribbon when displaying mock data

### 2.2 ✅ Chat Profile State Now Updates

**Status:** FIXED

The chat page now:
- Generates and tracks session_id for conversation continuity
- Extracts profile fields from conversation context
- Updates the profile sidebar in real-time as users provide information
- Passes session_id to results page for fetching actual recommendations
- Shows `has_recommendations` state from API response

### 2.3 ✅ Lambda Upload Now Processes File Content

**Status:** FIXED

The upload handler now:
- Extracts text from PDFs using `pypdf` library
- Sends actual document content to Claude for analysis
- Returns proper errors instead of fake data on failure
- Validates file size and content

### 2.4 ✅ Compare Page Now Fetches Real Data

**Status:** FIXED

The compare page now:
- Fetches recommendations from API using session_id
- Shows prominent warning banner when using example data
- Falls back gracefully with clear user messaging

### 2.5 ✅ File Content Processing Implemented

**Status:** FIXED

PDF upload flow now works:
1. File is stored to S3 ✓
2. Text is extracted from PDF using pypdf ✓
3. Actual content is sent to Claude ✓
4. Proper error handling instead of fake data ✓

### 2.6 ✅ Upload Base64 Handling Now Resilient

**Status:** FIXED

The upload handler now safely decodes base64 payloads even when API Gateway does **not** set `isBase64Encoded=true`, preventing PDF parsing failures from double-encoded bodies.

---

## Part 3: Security Issues

### 3.1 ✅ Hardcoded AWS Account ID - FIXED

**Status:** FIXED with environment variable fallback

```python
AGENT_ARN = os.environ.get('BEDROCK_AGENTCORE_ARN', 'arn:aws:bedrock-agentcore:...')
```

Now uses environment variable with fallback for local development.

### 3.2 ✅ Hardcoded S3 Bucket Name - FIXED

**Status:** FIXED with environment variable fallback

```python
UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET_NAME', 'cba-indicator-uploads')
```

### 3.3 ⚠️ Hardcoded API URL in Frontend - ACCEPTABLE FOR HACKATHON

**Status:** Intentionally kept for hackathon ease-of-use

The fallback URL allows the frontend to work out-of-the-box without configuration. For production, set `NEXT_PUBLIC_API_URL` environment variable.

### 3.4 ✅ Bare Exception with Data Fabrication - FIXED

**Status:** FIXED

Now uses specific `json.JSONDecodeError` handling and returns proper error responses instead of fabricated data.

### 3.5 ✅ Input Validation - FIXED

**Status:** FIXED

Lambda now validates:
- Message length (max 10,000 characters)
- Empty messages rejected
- File size (max 10MB)
- PDF content extraction errors handled properly

---

## Part 4: Architecture Issues

### 4.1 ✅ Global Mutable State in AgentCore - FIXED

**Status:** FIXED

Now uses session-scoped profile storage:

```python
session_profiles = {}  # Key: session_id, Value: profile dict

def get_session_profile(session_id: str) -> dict:
    """Get or create profile for a session."""
    if session_id not in session_profiles:
        session_profiles[session_id] = {...}
    return session_profiles[session_id]
```

Profile tools are created per-session with captured session_id.

### 4.2 ⚠️ No API Contract Between Frontend and Backend

**Status:** Remaining issue

The frontend expects certain response shapes but there's no shared type definition. Consider adding OpenAPI spec or shared types for production.

### 4.3 ✅ Results/Compare Pages Now Connected to Data Flow

**Status:** FIXED

The user flow now works:
1. Upload file or chat → Profile collected ✓
2. Agent recommends indicators → Response displayed in chat ✓
3. Chat tracks session_id and `has_recommendations` flag ✓
4. User clicks "View Recommendations" → Passes session_id ✓
5. Results page fetches from `/recommendations?session_id=xxx` ✓
6. Compare page also uses session_id for real data ✓

### 4.4 ⚠️ Lambda Recommendations Store is In-Memory

**Status:** Known limitation for hackathon

The `recommendations_store` dict in Lambda won't persist across invocations. For production, use DynamoDB. For hackathon demos, this works if requests hit the same Lambda instance.

---

## Part 5: Minor Issues

| File | Line | Issue |
|------|------|-------|
| `cba-frontend/app/chat/page.tsx` | 90-93 | Complex boolean logic for `isComplete` that's hard to follow |
| `cba-frontend/app/upload/page.tsx` | 51 | Uploads are PDF-only (no Excel support) |
| `cba-frontend/app/results/page.tsx` | 285 | Export button is disabled (coming soon) |
| `cba-frontend/app/compare/page.tsx` | 222, 323 | Export/selection actions are disabled (coming soon) |
| `agentcore-cba/.../main.py` | 16-22 | Import fallback creates dummy MCP client that does nothing silently |

---

## Recommendations

### ✅ Completed

1. **Security:** Environment variables with fallbacks for ARNs, bucket names
2. **Security:** Specific `json.JSONDecodeError` handling instead of bare except
3. **Security:** Input validation for message length and file size
4. **Security:** Proper error responses instead of fabricated data
5. **Feature:** PDF text extraction using pypdf
6. **Feature:** `/recommendations` endpoint for structured indicator data
7. **Feature:** Results/compare pages fetch from API with session_id
8. **Feature:** Chat page extracts profile from conversation context
9. **Feature:** Session ID tracking throughout the flow
10. **Feature:** Clear "DEMO DATA" warnings when using fallback data
11. **Architecture:** Session-scoped profile storage in AgentCore

### Remaining for Production

1. **Architecture:** Replace in-memory `recommendations_store` with DynamoDB
2. **Architecture:** Define API contracts with OpenAPI spec
3. **Architecture:** Add comprehensive logging and monitoring
4. **Feature:** Streaming responses in frontend for better UX
5. **Feature:** Export functionality for recommendations (PDF/CSV)
