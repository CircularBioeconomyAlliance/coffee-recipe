# CBA Indicator Selection Assistant - Code Review Report

## Executive Summary

The CBA Indicator Selection Assistant is an AI-powered tool for helping Circular Bioeconomy Alliance users find monitoring and evaluation indicators for sustainable agriculture projects. This review focuses on the **production stack**: the Next.js frontend, AWS Lambda backend, and Bedrock AgentCore agent.

> **Note:** The Streamlit app (`src/app.py`) and CLI agent (`src/agent.py`) are legacy/development components and are not covered in this review. The Next.js frontend in `cba-frontend/` is the only functional UI for production.

**Overall Assessment:** The production architecture is well-designed, but has critical security vulnerabilities that must be addressed, and the frontend is incomplete—several pages display mock data instead of actual API responses.

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
    
    if '/chat' in path:
        return handle_chat(event)
    elif '/upload' in path:
        return handle_upload(event)
    else:
        return {
            'statusCode': 404,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Not found'})
        }
```

**What works:**

- Clean separation of chat and upload handlers
- CORS headers properly configured
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
- File type validation (PDF, Excel)
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
  // ...
};
```

**What works:**

- Environment variable support for API URL
- Clean async/await pattern
- Error throwing for non-OK responses

---

## Part 2: What Doesn't Work Yet

### 2.1 Frontend Results Page - Disconnected from Backend

**Location:** [cba-frontend/app/results/page.tsx](cba-frontend/app/results/page.tsx)

The results page displays hardcoded mock data instead of actual recommendations from the AI:

```typescript
// Mock data
const mockIndicators: Indicator[] = [
  {
    id: 47,
    name: "Species Diversity Index",
    component: "Biotic",
    class: "Biodiversity",
    // ... hardcoded data
  },
  // More hardcoded indicators...
];
```

**Impact:** Users see the same 4 mock indicators regardless of their project profile or what the AI recommended. The entire purpose of the chat flow (gathering project details to recommend relevant indicators) is undermined.

**What's needed:** 
1. Backend endpoint to return structured indicator recommendations
2. Frontend state management to store recommendations from chat
3. API call to fetch recommendations by session ID

### 2.2 Chat Profile State Never Updates

**Location:** [cba-frontend/app/chat/page.tsx](cba-frontend/app/chat/page.tsx)

The profile sidebar shows "Pending..." forever because the `updateProfile` function is empty:

```typescript
const updateProfile = (userMessage: string) => {
  // Profile extraction is handled by the agent's backend tools
  // (set_project_location, set_project_commodity, etc.)
  // This function is kept for future manual profile updates if needed
};
```

**Impact:** Users cannot see their progress. The progress bar shows 0% even after answering all questions. The "Profile Complete" state is never reached.

**What's needed:** 
1. Backend should return profile state alongside chat responses
2. Frontend should parse and update profile state from responses
3. Or: Parse agent responses client-side to extract profile updates

### 2.3 Lambda Upload Doesn't Process File Content

**Location:** [lambda_function.py](lambda_function.py)

The upload handler stores the file to S3 but doesn't actually read its content:

```python
response = bedrock_runtime.invoke_model(
    modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
    body=json.dumps({
        "messages": [{
            "role": "user",
            "content": f"{prompt}\n\nDocument uploaded to: {s3_uri}"  # Just sends S3 path!
        }]
    })
)
```

**Impact:** The AI is told a document was uploaded to S3 but cannot read its contents. The extraction prompt asks Claude to analyze a document it cannot see. Results are either fabricated or based on filename guessing.

**What's needed:** 
1. Extract text from PDF using `pypdf` before sending to Claude
2. Or: Use Bedrock's document understanding capabilities with proper S3 access
3. Send actual document content in the prompt

### 2.4 Compare Page Uses Mock Data

**Location:** [cba-frontend/app/compare/page.tsx](cba-frontend/app/compare/page.tsx)

```typescript
// Mock data (same as results page)
const mockIndicators: Record<number, Indicator> = {
  47: { id: 47, name: "Species Diversity Index", ... },
  89: { id: 89, name: "Soil Organic Carbon", ... },
  // ...
};
```

**Impact:** Comparing indicators only works with the 4 hardcoded indicators. Any real recommendations from the AI cannot be compared.

**What's needed:** Same solution as results page—fetch real data from backend.

### 2.5 No File Content Processing

**Current state:** When a user uploads a PDF:
1. File is stored to S3 ✓
2. Claude is asked to extract information ✗ (only sees S3 path)
3. Response is parsed for profile data ✓
4. Fallback returns fake Brazil/Coffee data ✗

**What's needed:** Actual PDF text extraction before sending to Claude.

---

## Part 3: Security Issues (Must Fix)

### 3.1 Hardcoded AWS Account ID

**Location:** [lambda_function.py](lambda_function.py) line 10

```python
AGENT_ARN = 'arn:aws:bedrock-agentcore:us-west-2:687995992314:runtime/cbaindicatoragent_Agent-buoE288RIT'
```

**Risk:** AWS account ID `687995992314` is exposed. Anyone reading the code knows the account.

**Fix:**

```python
import os
AGENT_ARN = os.environ['BEDROCK_AGENTCORE_ARN']
```

### 3.2 Hardcoded S3 Bucket Name

**Location:** [lambda_function.py](lambda_function.py) line 11

```python
UPLOAD_BUCKET = 'cba-indicator-uploads'
```

**Risk:** Bucket name is publicly known, making it a target for enumeration attacks.

**Fix:**

```python
UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET_NAME']
```

### 3.3 Hardcoded API URL in Frontend

**Location:** [cba-frontend/lib/api.ts](cba-frontend/lib/api.ts) line 1

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://pjuuem2fn8.execute-api.us-west-2.amazonaws.com/prod";
```

**Risk:** Production API endpoint is hardcoded as fallback. Should require environment variable.

**Fix:**

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL;
if (!API_URL) throw new Error("NEXT_PUBLIC_API_URL environment variable is required");
```

### 3.4 Bare Exception with Data Fabrication

**Location:** [lambda_function.py](lambda_function.py) lines 119-124

```python
try:
    data = json.loads(extracted)
except:
    # Fallback if not valid JSON
    data = {'location': 'Brazil', 'commodity': 'Coffee', 'budget': '$50,000'}
```

**Risk:**

1. Bare `except:` catches everything including `KeyboardInterrupt`, `SystemExit`
2. On any error, the system silently returns fake data about Brazil/Coffee
3. Users may make decisions based on fabricated information

**Fix:**

```python
try:
    data = json.loads(extracted)
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse extraction result: {e}")
    return {
        'statusCode': 422,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Could not extract project information from document'})
    }
```

### 3.5 No Input Validation

**Location:** [lambda_function.py](lambda_function.py) `handle_chat` and `handle_upload`

Neither function validates:

- Message length (could be used for prompt injection or cost attacks)
- File size (Lambda has limits but should validate earlier)
- File content type (relies on frontend validation only)
- Session ID format (could be used for injection)

**What's needed:**

```python
def handle_chat(event):
    body = json.loads(event.get('body', '{}'))
    message = body.get('message', '')
    
    # Input validation
    if len(message) > 10000:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Message too long'})}
    if not message.strip():
        return {'statusCode': 400, 'body': json.dumps({'error': 'Message required'})}
    # ... continue
```

---

## Part 4: Architecture Issues

### 4.1 Global Mutable State in AgentCore

**Location:** [agentcore-cba/cbaindicatoragent/src/main.py](agentcore-cba/cbaindicatoragent/src/main.py) lines 64-71

```python
# CBA Project Profile State
project_profile = {
    "location": None,
    "commodity": None,
    "budget": None,
    "outcomes": None,
    "capacity": None
}
```

**Risk:** This is a module-level global dict. In a containerized environment with multiple concurrent requests, different users' profile data could overwrite each other.

**Fix:** Move profile state into the session context or use AgentCore Memory for per-session storage.

### 4.2 No API Contract Between Frontend and Backend

The frontend expects certain response shapes but there's no shared type definition:

- Chat response: `{ response: string, session_id: string }`
- Upload response: `{ found: {...}, missing: [...] }`

**Risk:** Frontend and backend can drift apart, causing runtime errors.

**What's needed:** Shared TypeScript/JSON Schema types, or OpenAPI spec.

### 4.3 Results/Compare Pages Not Connected to Data Flow

The user flow is:
1. Upload file or chat → Profile collected ✓
2. Agent recommends indicators → Response displayed in chat ✓
3. User clicks "View Recommendations" → **Shows mock data** ✗

There's no mechanism to:
- Store the agent's recommendations
- Retrieve them on the results page
- Pass them to the compare page

---

## Part 5: Minor Issues

| File | Line | Issue |
|------|------|-------|
| `lambda_function.py` | 55-56 | Markdown bold (`**`) stripped from responses—may break formatting |
| `cba-frontend/app/chat/page.tsx` | 90-93 | Complex boolean logic for `isComplete` that's hard to follow |
| `cba-frontend/app/upload/page.tsx` | 51 | MIME type list may not cover all Excel variants (`.xlsm`, `.xlsb`) |
| `agentcore-cba/.../main.py` | 16-22 | Import fallback creates dummy MCP client that does nothing silently |
| `cba-frontend/lib/api.ts` | 14-24 | `uploadFile` uses FormData but Lambda expects base64 |

---

## Recommendations

### Immediate (Before Production)

1. **Security:** Move all hardcoded ARNs, bucket names, and API URLs to environment variables
2. **Security:** Replace bare `except:` with specific `json.JSONDecodeError` handling
3. **Security:** Add input validation to Lambda handlers (message length, file size, content type)
4. **Security:** Remove fallback fake data—return errors instead

### Short-term (Next Sprint)

1. **Feature:** Implement actual PDF text extraction in Lambda upload handler
2. **Feature:** Add backend endpoint to return structured indicator recommendations
3. **Feature:** Connect results/compare pages to real API data
4. **Feature:** Implement profile state sync—backend returns profile in chat response

### Long-term (Technical Debt)

1. **Architecture:** Fix global mutable state in AgentCore—use session-scoped storage
2. **Architecture:** Define API contracts with shared types or OpenAPI spec
3. **Architecture:** Add comprehensive error handling and logging throughout
4. **Architecture:** Implement proper state management for the recommendation flow
