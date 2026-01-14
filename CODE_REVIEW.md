# CBA Indicator Selection Assistant - Code Review Report

## Executive Summary

The CBA Indicator Selection Assistant is an AI-powered tool for helping Circular Bioeconomy Alliance users find monitoring and evaluation indicators for sustainable agriculture projects. The codebase includes three parallel implementations: a CLI agent, a Streamlit web UI, and a production deployment on AWS Bedrock AgentCore with a Next.js frontend.

**Overall Assessment:** The core AI functionality is well-implemented, but the codebase has security vulnerabilities that must be addressed before production use, and several frontend features are incomplete or disconnected from the backend.

---

## Part 1: What Works Well

### 1.1 Core Agent Implementation (CLI)

The CLI agent in [src/agent.py](src/agent.py) is well-structured and functional:

```python
def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return "\n".join(text)
```

**What works:**

- Clean PDF and Excel text extraction using `pypdf` and `openpyxl`
- Proper file type detection and error handling
- Integration with Strands Agents framework
- Uses shared configuration from `config.py`
- Low temperature (0.2) for consistent, focused responses
- Clean command-line argument parsing for file input

### 1.2 Shared Configuration

The [src/config.py](src/config.py) centralizes key settings:

```python
# AWS Bedrock configuration
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
KNOWLEDGE_BASE_ID = "0ZQBMXEKDI"
AWS_REGION = "us-west-2"

# Set environment variables
os.environ["AWS_DEFAULT_REGION"] = AWS_REGION
os.environ["STRANDS_KNOWLEDGE_BASE_ID"] = KNOWLEDGE_BASE_ID

# Load system prompt from text file
PROMPTS_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "system.txt").read_text()
```

**What works:**

- Single source of truth for model ID and knowledge base ID
- System prompt stored as separate text file for easy editing
- Configuration reused across CLI and Streamlit apps

### 1.3 System Prompt Quality

The system prompt in [src/prompts/system.txt](src/prompts/system.txt) is comprehensive:

**What works:**

- Clear role definition ("CBA Indicator Selection assistant")
- Explicit knowledge base-first policy to prevent hallucination
- Required information checklist (location, project type, outcomes, budget, capacity)
- Structured output format for consistent responses
- Tool usage documentation
- 500-word limit for concise responses

### 1.4 Knowledge Base Tools (AgentCore)

The [agentcore-cba/cbaindicatoragent/src/kb_tool.py](agentcore-cba/cbaindicatoragent/src/kb_tool.py) provides well-designed search tools:

```python
@tool
def search_cba_indicators(query: str, max_results: int = 10) -> str:
    """
    Search the CBA M&E Framework Knowledge Base for relevant indicators and methods.
    
    Args:
        query: Natural language query about indicators, methods, or project requirements
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        Formatted string with relevant indicators and methods from the knowledge base
    """
```

**What works:**

- Four specialized search tools for different query types
- Proper use of the `@tool` decorator
- Formatted output with relevance scores
- Error handling with user-friendly messages

### 1.5 Streamlit UI Branding

The [src/app.py](src/app.py) has thorough CBA branding:

**What works:**

- Custom CSS with CBA color palette (#031f35 navy, #FBAD17 gold)
- Logo integration and mission statement
- Session management with UUID-based tracking
- Multi-session support with conversation history
- File upload with preview functionality
- Responsive layout with sidebar

### 1.6 Next.js Frontend Design

The frontend in [cba-frontend/](cba-frontend/) has excellent UI/UX:

**What works:**

- Beautiful CBA-branded dark theme
- Framer Motion animations for smooth transitions
- Responsive grid layouts
- Clear user flow: Home → Upload/Chat → Results → Compare
- Profile sidebar showing collected information
- Loading states and error handling in UI

### 1.7 Lambda Router Structure

The [lambda_function.py](lambda_function.py) has clean request routing:

```python
def lambda_handler(event, context):
    path = event.get('rawPath', event.get('path', ''))
    
    # Route to appropriate handler (handle both /chat and /prod/chat)
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

### 1.8 Test Coverage

The test files provide reasonable coverage:

**What works:**

- Unit tests for session title generation
- File processing tests for TXT, CSV, PDF, DOCX
- Session management logic tests
- Mock file class for testing uploads
- CBA branding verification tests

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
    cost: "Medium",
    accuracy: "High",
    ease: "Medium",
    principle: "Principle 2",
    criterion: "Criterion 2.1",
    priority: "Primary",
    definition: "Measures the variety and abundance of species...",
    methods: [
      { id: 1, name: "Random Walks", cost: "Low", accuracy: "Medium", ease: "High" },
      // ...
    ],
  },
  // More hardcoded indicators...
];
```

**Impact:** Users see the same 4 mock indicators regardless of their project profile or what the AI recommended. The entire purpose of the chat flow (gathering project details to recommend relevant indicators) is undermined.

**What's needed:** API endpoint to fetch recommendations based on session ID, then render actual results.

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

The sidebar displays profile fields but they never populate:

```typescript
<div className="space-y-4">
  <ProfileField
    icon={<MapPin className="w-4 h-4" />}
    label="Location"
    value={profile.location}  // Always undefined after initial load
  />
  <ProfileField
    icon={<span className="text-lg">🌾</span>}
    label="Commodity"
    value={profile.commodity}  // Always undefined
  />
  // ...
</div>
```

**Impact:** Users cannot see their progress. The progress bar shows 0% even after answering all questions.

**What's needed:** Parse backend responses to extract profile updates, or have the backend return structured profile data alongside the chat response.

### 2.3 Streamlit PDF/DOCX Extraction is Placeholder

**Location:** [src/app.py](src/app.py)

The Streamlit app claims to support PDF and DOCX but returns placeholder text:

```python
elif file_extension == 'pdf':
    # Handle PDF files - basic implementation
    # Note: For a full implementation, you'd want to use PyPDF2 or similar
    # For now, return a placeholder message
    return f"PDF file '{uploaded_file.name}' uploaded. PDF text extraction requires additional libraries (PyPDF2, pdfplumber). Content: [PDF content would be extracted here]"
    
elif file_extension == 'docx':
    # Handle DOCX files - basic implementation  
    # Note: For a full implementation, you'd want to use python-docx
    # For now, return a placeholder message
    return f"DOCX file '{uploaded_file.name}' uploaded. DOCX text extraction requires additional libraries (python-docx). Content: [DOCX content would be extracted here]"
```

**Irony:** The CLI agent in the same repo has working PDF extraction! The `pypdf` library is already in `pyproject.toml`.

**What's needed:** Import and use the `extract_pdf_text()` and `extract_excel_text()` functions from `agent.py`, or refactor into a shared utility module.

### 2.4 Lambda Upload Doesn't Process File Content

**Location:** [lambda_function.py](lambda_function.py)

The upload handler stores the file to S3 but doesn't actually read its content:

```python
response = bedrock_runtime.invoke_model(
    modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [{
            "role": "user",
            "content": f"{prompt}\n\nDocument uploaded to: {s3_uri}"  # Just sends S3 path, not content!
        }]
    })
)
```

**Impact:** The AI is told a document was uploaded to S3 but cannot read its contents. The extraction prompt asks Claude to analyze a document it cannot see.

**What's needed:** Either use Bedrock's document understanding capabilities with the S3 URI, or extract text from the PDF before sending to Claude.

### 2.5 Compare Page Uses Same Mock Data

**Location:** [cba-frontend/app/compare/page.tsx](cba-frontend/app/compare/page.tsx)

```typescript
// Mock data (same as results page)
const mockIndicators: Record<number, Indicator> = {
  47: {
    id: 47,
    name: "Species Diversity Index",
    // ... same hardcoded data
  },
  // ...
};
```

**Impact:** Comparing indicators only works with the 4 hardcoded indicators. Any real recommendations from the AI cannot be compared.

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
AGENT_ARN = os.environ['BEDROCK_AGENTCORE_ARN']
```

### 3.2 Hardcoded S3 Bucket Name

**Location:** [lambda_function.py](lambda_function.py) line 11

```python
UPLOAD_BUCKET = 'cba-indicator-uploads'
```

**Risk:** Bucket name is publicly known, making it a target.

**Fix:**

```python
UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET_NAME']
```

### 3.3 Bare Exception with Data Fabrication

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

### 3.4 No Input Validation

**Location:** [lambda_function.py](lambda_function.py) `handle_chat` and `handle_upload`

Neither function validates:

- Message length (could be used for prompt injection or cost attacks)
- File size (Lambda has limits but should validate earlier)
- File content type (relies on frontend validation only)
- Session ID format (could be used for injection)

---

## Part 4: Architecture Inconsistencies

### 4.1 Three Different Agent Implementations

| Component | File | Model ID | KB Access | System Prompt |
|-----------|------|----------|-----------|---------------|
| CLI | `src/agent.py` | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | `memory` tool | `src/prompts/system.txt` |
| Streamlit | `src/app.py` | Same as CLI (via config) | `memory` tool | Same as CLI |
| AgentCore | `agentcore-cba/.../main.py` | `global.anthropic.claude-sonnet-4-5-20250929-v1:0` | Custom `kb_tool.py` | Inline 30-line prompt |

**Problems:**

1. Model prefix differs (`us.` vs `global.`)
2. AgentCore has a completely different system prompt that doesn't match the CLI prompt
3. KB access method differs (generic `memory` tool vs specialized search tools)
4. No shared code between implementations

### 4.2 Test Expectations Don't Match Implementation

**Location:** [tests/test_functions.py](tests/test_functions.py) vs [src/app.py](src/app.py)

Test expects:

```python
# test_functions.py line 18-19
if not first_message or not first_message.strip():
    return "New Chat"
```

Implementation returns:

```python
# app.py line 302-303
if not first_message or not first_message.strip():
    return "New Conversation"
```

**Impact:** Tests would fail if they actually imported from the app module with the real implementation.

### 4.3 Global Mutable State in AgentCore

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

---

## Part 5: Minor Issues

| File | Line | Issue |
|------|------|-------|
| `src/config.py` | 12-13 | Sets environment variables at import time (side effect in module load) |
| `cba-frontend/app/chat/page.tsx` | 90-93 | Complex boolean logic for `isComplete` that's hard to follow |
| `cba-frontend/app/upload/page.tsx` | 51 | MIME type list may not cover all Excel variants (`.xlsm`, `.xlsb`) |
| `agentcore-cba/.../main.py` | 16-22 | Import fallback creates dummy MCP client that does nothing |
| `src/app.py` | 382 | `@st.cache_resource` on `get_agent()` means one agent instance shared across all users |

---

## Recommendations

### Immediate (Before Production)

1. Move all hardcoded credentials to environment variables
2. Replace bare `except:` with specific exception handling
3. Add input validation to Lambda handlers
4. Add logging for errors instead of silent failures

### Short-term (Next Sprint)

1. Connect results/compare pages to actual API data
2. Implement profile state sync between frontend and backend
3. Reuse PDF extraction code in Streamlit app
4. Fix test expectations to match implementation

### Long-term (Technical Debt)

1. Create shared agent module used by all three implementations
2. Consolidate system prompts into single source of truth
3. Add proper session-scoped state management in AgentCore
4. Implement comprehensive API contracts between frontend and backend
