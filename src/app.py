"""
Circular Bioeconomy Alliance Chat App - A nature-focused chat application with session management and file upload capabilities.
"""

import streamlit as st
import uuid
import datetime
import io
import csv
import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from strands import Agent
from strands_tools import memory, use_llm

# Load system prompt from text file (relative to this file in src/)
PROMPT_PATH = Path(__file__).parent / "prompts" / "system.txt"
SYSTEM_PROMPT = PROMPT_PATH.read_text()

# Configuration
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
KNOWLEDGE_BASE_ID = "CXRV29T1AF"

# Set AWS region and knowledge base ID
os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
os.environ["STRANDS_KNOWLEDGE_BASE_ID"] = KNOWLEDGE_BASE_ID

# Set up page configuration
st.set_page_config(
    page_title="CBA Chat Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for CBA branding and color scheme
st.markdown("""
<style>
    /* CBA Color Palette - Official brand colors */
    :root {
        --cba-main-background: #031f35;
        --cba-accent-gold: #FBAD17;
        --cba-text-light: #FFFFFF;
        --cba-text-muted: #B0B0B0;
        --cba-card-background: #0a2a42;
        --cba-border-color: #1a3a52;
        --cba-hover-background: #FBAD17;
        --cba-selected-background: #FBAD17;
    }
    
    /* Main app styling */
    .main .block-container {
        background-color: var(--cba-main-background);
        padding-top: 2rem;
        color: var(--cba-text-light);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--cba-main-background);
    }
    
    /* Override Streamlit's default styling */
    .stApp {
        background-color: var(--cba-main-background);
    }
    
    /* Chat input styling */
    .stChatInput > div > div > div > div {
        background-color: var(--cba-card-background);
        border: 1px solid var(--cba-border-color);
        color: var(--cba-text-light);
    }
    
    /* Text styling */
    .stMarkdown, .stText, p, div {
        color: var(--cba-text-light);
    }
    
    /* CBA Logo and Header Styling */
    .cba-header {
        text-align: center;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        border: 2px solid var(--cba-accent-gold);
    }
    
    .cba-logo-img {
        width: 100%;
        max-width: 280px;
        height: auto;
        border-radius: 8px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .cba-logo-img:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(251, 173, 23, 0.3);
    }
    
    /* Principles section styling */
    .cba-principles {
        background-color: var(--cba-card-background);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--cba-accent-gold);
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .cba-principles h4 {
        color: var(--cba-accent-gold);
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .cba-principles ul {
        margin: 0;
        padding-left: 1rem;
        font-size: 0.85rem;
        color: var(--cba-text-light);
    }
    
    .cba-principles li {
        margin-bottom: 0.3rem;
    }
    
    .cba-principles p {
        color: var(--cba-text-muted);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--cba-card-background);
        color: var(--cba-text-light);
        border: 1px solid var(--cba-border-color);
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--cba-hover-background);
        color: var(--cba-main-background);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(251, 173, 23, 0.3);
        border-color: var(--cba-accent-gold);
    }
    
    .stButton > button:active,
    .stButton > button:focus {
        background-color: var(--cba-selected-background);
        color: var(--cba-main-background);
        border-color: var(--cba-accent-gold);
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 10px;
        margin-bottom: 1rem;
        background-color: var(--cba-card-background);
        border: 1px solid var(--cba-border-color);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background-color: var(--cba-card-background);
        border-radius: 8px;
        padding: 1rem;
        border: 2px dashed var(--cba-accent-gold);
    }
    
    /* Success message styling */
    .stSuccess {
        background-color: var(--cba-card-background);
        color: var(--cba-text-light);
        border-radius: 6px;
        border-left: 4px solid var(--cba-accent-gold);
    }
    
    /* Info message styling */
    .stInfo {
        background-color: var(--cba-card-background);
        color: var(--cba-text-light);
        border-radius: 6px;
        border-left: 4px solid var(--cba-accent-gold);
    }
    
    /* Main title styling */
    h1 {
        color: var(--cba-accent-gold);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Section headers */
    h2, h3 {
        color: var(--cba-accent-gold);
    }
    
    /* Divider styling */
    hr {
        border-color: var(--cba-border-color);
        margin: 1.5rem 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: var(--cba-card-background);
        color: var(--cba-text-light);
    }
    
    .streamlit-expanderContent {
        background-color: var(--cba-card-background);
        border: 1px solid var(--cba-border-color);
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: var(--cba-card-background);
        color: var(--cba-text-light);
        border: 1px solid var(--cba-border-color);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables for the chat app."""
    
    # Initialize sessions dictionary in session state (Requirement 4.1)
    if "sessions" not in st.session_state:
        st.session_state.sessions = {}
    
    # Set up current_session_id tracking (Requirement 4.2)
    if "current_session_id" not in st.session_state:
        # Create initial session if none exists
        initial_session_id = str(uuid.uuid4())
        st.session_state.current_session_id = initial_session_id
        st.session_state.sessions[initial_session_id] = {
            "title": "New Conversation",
            "created_at": datetime.datetime.now(),
            "messages": [],
            "uploaded_files": []
        }
    
    # Initialize messages list for current session (Requirement 4.3)
    if "messages" not in st.session_state:
        current_session = st.session_state.sessions.get(st.session_state.current_session_id, {})
        st.session_state.messages = current_session.get("messages", [])

# Session management functions
def create_new_session():
    """
    Create a new chat session with unique ID and empty messages.
    Sets the new session as the current active session.
    Requirement 2.1: WHEN a user clicks new chat, THE Chat_App SHALL create a new session with unique ID
    """
    # Generate UUID for new session
    new_session_id = str(uuid.uuid4())
    
    # Create session data structure with empty messages
    new_session = {
        "title": "New Conversation",
        "created_at": datetime.datetime.now(),
        "messages": [],
        "uploaded_files": []
    }
    
    # Add to sessions dictionary
    st.session_state.sessions[new_session_id] = new_session
    
    # Set as current active session
    st.session_state.current_session_id = new_session_id
    st.session_state.messages = []
    
    return new_session_id

def switch_session(session_id):
    """
    Switch to a different session by loading its messages and updating current session state.
    Requirement 2.2: WHEN a user selects a session, THE Chat_App SHALL load that session's messages
    """
    # Validate session exists
    if session_id not in st.session_state.sessions:
        st.error(f"Session {session_id} not found")
        return False
    
    # Load messages from selected session
    selected_session = st.session_state.sessions[session_id]
    
    # Update current session state
    st.session_state.current_session_id = session_id
    st.session_state.messages = selected_session["messages"].copy()
    
    return True

def generate_session_title(first_message):
    """
    Generate a readable session title from the first message.
    Requirement 2.4: THE Chat_App SHALL auto-generate session titles from first message
    """
    if not first_message or not first_message.strip():
        return "New Conversation"
    
    # Extract first few words from first message
    words = first_message.strip().split()
    
    # Create readable session title (limit to first 5 words, max 50 characters)
    if len(words) <= 5:
        title = " ".join(words)
    else:
        title = " ".join(words[:5]) + "..."
    
    # Ensure title doesn't exceed 50 characters
    if len(title) > 50:
        title = title[:47] + "..."
    
    return title

def extract_file_content(uploaded_file):
    """
    Extract text content from uploaded files of different types.
    Handles TXT, PDF, DOCX, and CSV files.
    Requirement 3.3: THE Chat_App SHALL include file content in LLM context
    """
    if uploaded_file is None:
        return ""
    
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'txt':
            # Handle TXT files
            content = uploaded_file.read().decode('utf-8')
            return content
            
        elif file_extension == 'csv':
            # Handle CSV files
            uploaded_file.seek(0)  # Reset file pointer
            content = uploaded_file.read().decode('utf-8')
            
            # Parse CSV and convert to readable text
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)
            
            if not rows:
                return "Empty CSV file"
            
            # Format CSV as text with headers and data
            formatted_content = []
            if len(rows) > 0:
                headers = rows[0]
                formatted_content.append("CSV Headers: " + ", ".join(headers))
                formatted_content.append("\nData:")
                
                # Include first 10 rows of data to avoid overwhelming context
                for i, row in enumerate(rows[1:11], 1):
                    formatted_content.append(f"Row {i}: " + ", ".join(row))
                
                if len(rows) > 11:
                    formatted_content.append(f"... and {len(rows) - 11} more rows")
            
            return "\n".join(formatted_content)
            
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
            
        else:
            return f"Unsupported file type: {file_extension}"
            
    except Exception as e:
        return f"Error processing file '{uploaded_file.name}': {str(e)}"

@st.cache_resource
def get_agent():
    """
    Initialize and cache the Strands agent for the CBA chatbot.
    Uses st.cache_resource to ensure the agent is only created once per session.
    """
    agent = Agent(
        model=MODEL_ID,
        system_prompt=SYSTEM_PROMPT,
        tools=[memory, use_llm],
    )
    return agent


def get_agent_response(user_message, file_content=None):
    """
    Get response from the Strands agent with CBA Knowledge Base integration.
    Requirement 1.2: WHEN the LLM responds, THE Chat_App SHALL stream the response
    Requirement 3.3: THE Chat_App SHALL include file content in LLM context
    """
    agent = get_agent()

    # Build the prompt with file context if available
    if file_content and file_content.strip():
        full_prompt = f"""User question: {user_message}

The user has also provided the following document content for context:
---
{file_content[:2000]}{'...[truncated]' if len(file_content) > 2000 else ''}
---

Please consider this document when answering."""
    else:
        full_prompt = user_message

    # Get response from agent
    result = agent(full_prompt)

    # Extract text response from agent result
    response_text = str(result)

    # Yield response in chunks for streaming effect
    words = response_text.split()
    for i in range(0, len(words), 3):  # Yield 3 words at a time
        chunk = " ".join(words[i:i+3]) + " "
        yield chunk

def main():
    """
    Main function that orchestrates the entire Streamlit chat application.
    
    This function:
    - Initializes session state (Requirement 4.1, 4.2, 4.3)
    - Renders sidebar components (Requirements 2.1, 2.3, 3.1, 3.2)
    - Renders main chat area (Requirements 1.1, 1.3)
    - Handles user interactions (Requirements 1.1, 1.2, 1.4)
    """
    
    # Set up main title
    st.title("🌍 Circular Bioeconomy Alliance Chat Assistant")
    
    # Initialize session state
    initialize_session_state()

    # Render sidebar components
    with st.sidebar:
        # CBA Logo and Header
        st.markdown("""
        <div class="cba-header">
            <img src="https://circularbioeconomyalliance.org/wp-content/uploads/2021/10/circular_bioeconomy_alliance_social_share.png" 
                 alt="Circular Bioeconomy Alliance Logo" 
                 class="cba-logo-img">
        </div>
        """, unsafe_allow_html=True)
        
        # CBA Principles Section
        st.markdown("""
        <div class="cba-principles">
            <h4>Our Mission</h4>
            <ul>
                <li><strong>Re-Nature:</strong> Place nature at the center of our economy</li>
                <li><strong>Re-Think:</strong> Transform systems for sustainability</li>
                <li><strong>Re-Activate:</strong> Create regenerative, inclusive solutions</li>
            </ul>
            <p style="font-size: 0.8rem; margin-top: 0.5rem; font-style: italic;">
                Founded by His Majesty King Charles III to accelerate the transition to a climate-neutral, 
                nature-positive economy that prospers in harmony with our planet.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.header("Chat Sessions")
        
        # 4.1 Create new chat button (Requirement 2.1)
        if st.button("🌿 New Conversation", use_container_width=True):
            create_new_session()
            st.rerun()
        
        # 4.2 Display session list (Requirements 2.3)
        st.subheader("Your Conversations")
        
        if st.session_state.sessions:
            # Sort sessions by creation time (newest first)
            sorted_sessions = sorted(
                st.session_state.sessions.items(),
                key=lambda x: x[1]["created_at"],
                reverse=True
            )
            
            for session_id, session_data in sorted_sessions:
                # Update session title if it has messages and is still "New Conversation"
                if session_data["messages"] and session_data["title"] == "New Conversation":
                    first_message = session_data["messages"][0]["content"]
                    session_data["title"] = generate_session_title(first_message)
                
                # Create a button for each session
                is_current = session_id == st.session_state.current_session_id
                button_label = f"{'🌱 ' if is_current else '🌿 '}{session_data['title']}"
                
                if st.button(button_label, key=f"session_{session_id}", use_container_width=True):
                    if session_id != st.session_state.current_session_id:
                        switch_session(session_id)
                        st.rerun()
        else:
            st.info("No conversations yet. Start a new conversation to explore circular bioeconomy topics!")
        
        # 4.3 Add file uploader (Requirements 3.1, 3.2)
        st.divider()
        st.subheader("📎 Document Upload")
        
        uploaded_file = st.file_uploader(
            "Upload documents for context",
            type=["pdf", "txt", "docx", "csv"],
            help="Share research papers, reports, or data files to enhance our conversation about circular bioeconomy solutions"
        )
        
        # Display uploaded filename (Requirement 3.2)
        if uploaded_file is not None:
            st.success(f"📄 {uploaded_file.name}")
            
            # Extract and store file content in session state (Requirement 3.3)
            if not hasattr(st.session_state, 'uploaded_file') or st.session_state.uploaded_file != uploaded_file:
                # Process the file and extract content
                file_content = extract_file_content(uploaded_file)
                
                # Store both the file and its content in session state
                st.session_state.uploaded_file = uploaded_file
                st.session_state.file_content = file_content
                
                # Also store in current session's uploaded_files list
                current_session = st.session_state.sessions[st.session_state.current_session_id]
                current_session["uploaded_files"] = [{
                    "name": uploaded_file.name,
                    "content": file_content
                }]
                
                # Show a preview of the extracted content
                with st.expander("📄 Document Preview"):
                    st.text_area("Extracted content:", file_content[:500] + "..." if len(file_content) > 500 else file_content, height=100, disabled=True)
            
        elif hasattr(st.session_state, 'uploaded_file') and st.session_state.uploaded_file is not None:
            # Show previously uploaded file if still in session
            st.info(f"📄 {st.session_state.uploaded_file.name}")
            
            # Show content preview if available
            if hasattr(st.session_state, 'file_content'):
                with st.expander("📄 Document Preview"):
                    content = st.session_state.file_content
                    st.text_area("Extracted content:", content[:500] + "..." if len(content) > 500 else content, height=100, disabled=True)
        else:
            st.session_state.uploaded_file = None
            if hasattr(st.session_state, 'file_content'):
                st.session_state.file_content = None

    # Render main chat area
    st.header("💬 Circular Bioeconomy Conversation")
    
    # Add helpful context message for new sessions
    if not st.session_state.messages:
        st.info("""
        🌱 **Welcome to the Circular Bioeconomy Alliance Chat Assistant!**
        
        I'm here to help you explore topics related to:
        • **Sustainable resource management** and circular economy principles
        • **Nature-based solutions** for climate and biodiversity challenges  
        • **Regenerative practices** in agriculture, forestry, and industry
        • **Innovative financing** for nature-positive investments
        • **Community-led initiatives** and indigenous knowledge systems
        
        Feel free to ask questions, share documents, or discuss how we can build a more sustainable future together!
        """)

    # 6.1 Display chat messages (Requirements 1.1, 1.3)
    # Use st.chat_message to show message history
    # Display both user and assistant messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # 6.2 Implement chat input handling (Requirements 1.1, 1.4)
    # Use st.chat_input for user input
    # Add messages to current session
    if prompt := st.chat_input("Share your thoughts on circular bioeconomy, sustainability, or nature-based solutions..."):
        # Add user message to current session
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        
        # Update the session in the sessions dictionary
        current_session = st.session_state.sessions[st.session_state.current_session_id]
        current_session["messages"] = st.session_state.messages.copy()
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(prompt)
        
        # Update session title if this is the first message
        if len(st.session_state.messages) == 1:
            new_title = generate_session_title(prompt)
            current_session["title"] = new_title
        
        # 6.3 Add LLM response simulation (Requirements 1.2, 3.3)
        # Create placeholder LLM response function
        # Use st.write_stream for streaming effect
        # Include file content in context when available
        with st.chat_message("assistant"):
            # Get file content if available
            file_content = getattr(st.session_state, 'file_content', None)
            
            # Generate and stream the response from the Strands agent
            response_generator = get_agent_response(prompt, file_content)
            response = st.write_stream(response_generator)
            
            # Add assistant response to session
            assistant_message = {"role": "assistant", "content": response}
            st.session_state.messages.append(assistant_message)
            
            # Update the session in the sessions dictionary
            current_session["messages"] = st.session_state.messages.copy()

if __name__ == "__main__":
    main()