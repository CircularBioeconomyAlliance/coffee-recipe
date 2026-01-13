# Project Structure

## Directory Organization

```
coffee-recipe/
├── src/                    # Main application code
│   ├── __init__.py
│   ├── agent.py           # CLI chatbot entry point
│   ├── app.py             # Streamlit web UI
│   ├── config.py          # Shared configuration
│   └── prompts/           # System prompts (plain text)
│       ├── system.txt     # Main system prompt
│       └── prompt_original.txt
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_functions.py  # Unit tests for core functions
│   ├── test_cba_ui.py     # UI branding tests
│   └── test_chat_app.py   # Integration tests
├── cba_inputs/            # Reference documents
│   ├── CBA ME Background.pdf
│   ├── CBA ME Indicators List.xlsx
│   ├── Indicators for Use Case Regenerative Cotton in Chad.xlsx
│   └── Use Case Regenerative Cotton in Chad.pdf
├── .kiro/                 # Kiro IDE configuration
│   └── steering/          # AI assistant guidance
├── pyproject.toml         # Python project configuration
├── uv.lock               # Dependency lock file
├── README.md             # Project documentation
└── CLAUDE.md             # Claude-specific guidance
```

## Code Organization Patterns

### Entry Points
- **`src/agent.py`**: CLI interface with argument parsing for file uploads
- **`src/app.py`**: Streamlit web application with session management

### Shared Components
- **`src/config.py`**: Centralized configuration (model ID, KB ID, prompts)
- **`src/prompts/`**: Plain text prompt files (easier editing than Python strings)

### Testing Strategy
- **Unit tests**: `test_functions.py` - Core logic without Streamlit dependencies
- **UI tests**: `test_cba_ui.py` - Branding and interface components
- **Integration tests**: `test_chat_app.py` - End-to-end functionality

## File Naming Conventions

- Python modules: lowercase with underscores (`agent.py`, `config.py`)
- Test files: `test_` prefix matching module name
- Prompt files: descriptive names with `.txt` extension
- Documentation: uppercase for project-level files (`README.md`, `CLAUDE.md`)

## Import Patterns

### Internal Imports
```python
# Relative imports within src/
from config import MODEL_ID, KNOWLEDGE_BASE_ID, SYSTEM_PROMPT

# Path manipulation for imports
sys.path.insert(0, str(Path(__file__).parent))
```

### External Dependencies
```python
# Strands framework
from strands import Agent
from strands_tools import memory, use_llm, current_time, file_write

# File processing
import openpyxl
from pypdf import PdfReader

# Streamlit
import streamlit as st
```

## Configuration Management

- Environment variables set programmatically in `config.py`
- AWS credentials provided externally (never committed)
- Model and Knowledge Base IDs centralized in config
- System prompts loaded from text files for easy editing

## File Processing Support

- **PDF**: Text extraction using `pypdf`
- **Excel**: Data extraction using `openpyxl`
- **CSV**: Built-in Python csv module
- **TXT**: Direct UTF-8 decoding
- File content integrated into LLM context with size limits