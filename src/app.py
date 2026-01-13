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
from strands_tools import use_llm

# Import shared configuration
from config import MODEL_ID, KNOWLEDGE_BASE_ID, SYSTEM_PROMPT

# Import workflow helper functions
from workflow import (
    upload_document_to_s3,
    query_knowledge_base,
    extract_project_info,
    get_missing_fields,
    is_info_complete
)

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
    
    # Initialize workflow state variables (Requirements 1.3, 1.5, 9.1)
    if "workflow_phase" not in st.session_state:
        st.session_state.workflow_phase = "upload"
    
    if "project_info" not in st.session_state:
        st.session_state.project_info = {
            "location": None,
            "project_type": None,
            "outcomes": [],
            "budget": None,
            "capacity": None,
            "documents_uploaded": False
        }
    
    if "indicators" not in st.session_state:
        st.session_state.indicators = []

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
        tools=[use_llm],
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
    - Routes to phase-based UI (Requirements 1.1, 10.1)
    """
    
    # Set up main title
    st.title("🌍 Circular Bioeconomy Alliance Chat Assistant")
    
    # Initialize session state
    initialize_session_state()
    
    # 4.1 Phase detection - Get current workflow phase and route to appropriate UI
    # Requirements: 1.1, 10.1
    phase = st.session_state.workflow_phase

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

    # Route to appropriate UI based on workflow phase
    if phase == 'upload':
        render_upload_phase()
    elif phase == 'extract':
        render_extract_phase()
    elif phase == 'ask':
        render_ask_phase()
    elif phase == 'retrieve':
        render_retrieve_phase()
    elif phase == 'chat':
        render_chat_phase()
    else:
        st.error(f"Unknown workflow phase: {phase}")


def render_upload_phase():
    """
    Render upload phase UI with error handling.
    Requirements: 2.1, 2.5, 10.3
    """
    st.header("📤 Document Upload")
    
    st.info("""
    🌱 **Welcome to the CBA Indicator Selection Assistant!**
    
    To help you find the most relevant sustainability indicators, you can:
    - **Upload project documents** (PDF, Excel, CSV, TXT) for automatic information extraction
    - **Skip to manual entry** if you prefer to provide information directly
    """)
    
    # Show file uploader prominently
    uploaded_file = st.file_uploader(
        "Upload your project documents",
        type=["pdf", "txt", "csv", "xlsx"],
        help="Upload project proposals, reports, or data files to help us understand your project context"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # On upload: extract text, transition to 'extract'
        if uploaded_file is not None:
            if st.button("📄 Process Document", use_container_width=True, type="primary"):
                try:
                    # Extract file content
                    file_content = extract_file_content(uploaded_file)
                    
                    # Check if extraction was successful
                    if file_content and not file_content.startswith("Error"):
                        # Store in session state
                        st.session_state.file_content = file_content
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.session_state.project_info['documents_uploaded'] = True
                        
                        # Transition to extract phase
                        st.session_state.workflow_phase = 'extract'
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to process file: {file_content}")
                        st.info("💡 Please try a different file or skip to manual entry.")
                
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                    st.info("💡 Please try a different file or skip to manual entry.")
    
    with col2:
        # On skip: transition to 'ask'
        if st.button("⏭️ Skip to Manual Entry", use_container_width=True):
            st.session_state.project_info['documents_uploaded'] = False
            st.session_state.workflow_phase = 'ask'
            st.rerun()


def render_extract_phase():
    """
    Render extract phase UI with error handling.
    Requirements: 3.1, 3.4, 3.5
    """
    st.header("🔍 Extracting Information")
    
    # Show extracting message
    with st.spinner("Analyzing your document and extracting project information..."):
        # Get file content from session state
        file_content = st.session_state.get('file_content', '')
        
        if file_content:
            try:
                # Call extract_project_info()
                extracted_info = extract_project_info(file_content)
                
                # Check if any information was extracted
                has_info = any(
                    value is not None and value != [] and value != ''
                    for key, value in extracted_info.items()
                )
                
                if has_info:
                    # Update project_info in session state
                    for key, value in extracted_info.items():
                        if value is not None:
                            st.session_state.project_info[key] = value
                    
                    st.success("✅ Information extracted successfully!")
                    
                    # Show what was extracted
                    st.subheader("Extracted Information:")
                    for key, value in extracted_info.items():
                        if value is not None and value != [] and value != '':
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                else:
                    st.warning("⚠️ Could not extract information from the document. You'll be able to enter information manually.")
            
            except Exception as e:
                st.error(f"❌ Error during extraction: {str(e)}")
                st.info("Don't worry - you can still provide information manually in the next step.")
        else:
            st.warning("No document content found. Proceeding to manual entry.")
    
    # Transition to 'ask' phase
    st.session_state.workflow_phase = 'ask'
    st.rerun()


def render_ask_phase():
    """
    Render ask phase UI.
    Requirements: 4.2, 4.3, 4.4, 10.4
    """
    st.header("❓ Project Information")
    
    # Get missing fields
    missing = get_missing_fields(st.session_state.project_info)
    
    if missing:
        # Display missing fields clearly
        st.info(f"📋 Please provide the following information to help us recommend relevant indicators:")
        
        # Show form for each missing field
        with st.form("project_info_form"):
            form_data = {}
            
            for field in missing:
                if field == 'location':
                    form_data[field] = st.text_input(
                        "Location",
                        placeholder="e.g., Chad, West Africa",
                        help="Geographic location of your project"
                    )
                elif field == 'project_type':
                    form_data[field] = st.text_input(
                        "Project Type",
                        placeholder="e.g., regenerative cotton farming",
                        help="Type of circular bioeconomy project"
                    )
                elif field == 'outcomes':
                    outcomes_text = st.text_area(
                        "Expected Outcomes",
                        placeholder="e.g., improved soil health, reduced water use, increased biodiversity",
                        help="List your expected project outcomes (one per line or comma-separated)"
                    )
                    # Convert text to list
                    if outcomes_text:
                        form_data[field] = [o.strip() for o in outcomes_text.replace('\n', ',').split(',') if o.strip()]
                    else:
                        form_data[field] = None
                elif field == 'budget':
                    form_data[field] = st.selectbox(
                        "Budget Level",
                        options=['', 'low', 'medium', 'high'],
                        help="Available budget for monitoring and evaluation"
                    )
                    if form_data[field] == '':
                        form_data[field] = None
                elif field == 'capacity':
                    form_data[field] = st.selectbox(
                        "Technical Capacity",
                        options=['', 'basic', 'intermediate', 'advanced'],
                        help="Technical capacity for data collection and analysis"
                    )
                    if form_data[field] == '':
                        form_data[field] = None
            
            # Submit button
            submitted = st.form_submit_button("Continue", use_container_width=True, type="primary")
            
            if submitted:
                # Update project_info with form data
                for field, value in form_data.items():
                    if value is not None and value != '' and value != []:
                        st.session_state.project_info[field] = value
                
                # Check if complete
                if is_info_complete(st.session_state.project_info):
                    # Transition to 'retrieve'
                    st.session_state.workflow_phase = 'retrieve'
                    st.rerun()
                else:
                    # Stay in 'ask' - will show remaining missing fields
                    st.rerun()
    else:
        # All information is complete
        st.success("✅ All required information has been collected!")
        
        # Show summary
        st.subheader("Project Summary:")
        for key, value in st.session_state.project_info.items():
            if key != 'documents_uploaded' and value is not None and value != [] and value != '':
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Button to proceed
        if st.button("🔎 Find Indicators", use_container_width=True, type="primary"):
            st.session_state.workflow_phase = 'retrieve'
            st.rerun()


def render_retrieve_phase():
    """
    Render retrieve phase UI with error handling and timeout.
    Requirements: 5.3, 5.5, 8.4
    """
    st.header("🔎 Retrieving Indicators")
    
    # Show retrieving message
    with st.spinner("Searching the CBA Knowledge Base for relevant indicators..."):
        # Build query from project_info
        project_info = st.session_state.project_info
        
        query_parts = []
        if project_info.get('project_type'):
            query_parts.append(f"project type: {project_info['project_type']}")
        if project_info.get('location'):
            query_parts.append(f"location: {project_info['location']}")
        if project_info.get('outcomes'):
            outcomes_str = ', '.join(project_info['outcomes'])
            query_parts.append(f"outcomes: {outcomes_str}")
        if project_info.get('budget'):
            query_parts.append(f"budget: {project_info['budget']}")
        if project_info.get('capacity'):
            query_parts.append(f"technical capacity: {project_info['capacity']}")
        
        query = "Find relevant sustainability indicators for a circular bioeconomy project with " + "; ".join(query_parts)
        
        try:
            # Call query_knowledge_base() with timeout
            response = query_knowledge_base(query, timeout=30)
            
            # Extract indicators from response
            # The response structure from retrieve_and_generate includes output text
            if 'output' in response and 'text' in response['output']:
                indicators_text = response['output']['text']
                
                # Store indicators in session state
                st.session_state.indicators = [{
                    'query': query,
                    'response': indicators_text,
                    'retrieved_at': datetime.datetime.now()
                }]
                
                st.success("✅ Indicators retrieved successfully!")
            else:
                st.warning("⚠️ No indicators found. The Knowledge Base may not have relevant information for your project.")
                st.info("You can still proceed to ask questions, or go back to adjust your project information.")
                st.session_state.indicators = []
        
        except Exception as e:
            error_message = str(e)
            st.error(f"❌ Error retrieving indicators: {error_message}")
            
            # Provide helpful guidance based on error type
            if "timed out" in error_message.lower():
                st.info("💡 The query took too long. Try simplifying your project description or try again.")
            elif "not found" in error_message.lower():
                st.info("💡 Please verify your AWS configuration and Knowledge Base ID.")
            elif "access denied" in error_message.lower():
                st.info("💡 Please check your AWS credentials and permissions.")
            else:
                st.info("💡 Please try again or contact support if the issue persists.")
            
            st.session_state.indicators = []
            
            # Offer option to retry or go back
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again", use_container_width=True):
                    st.rerun()
            with col2:
                if st.button("⬅️ Go Back", use_container_width=True):
                    st.session_state.workflow_phase = 'ask'
                    st.rerun()
            
            # Don't auto-transition on error - let user decide
            return
    
    # Transition to 'chat' phase only if successful
    st.session_state.workflow_phase = 'chat'
    st.rerun()


def render_chat_phase():
    """
    Render chat phase UI with error handling.
    Requirements: 6.2, 6.4, 10.5, 8.4
    """
    st.header("💬 Indicator Discussion")
    
    # Display retrieved indicators
    if st.session_state.indicators:
        st.subheader("📊 Recommended Indicators")
        
        for idx, indicator_data in enumerate(st.session_state.indicators):
            with st.expander(f"Indicator Set {idx + 1}", expanded=(idx == 0)):
                st.write(indicator_data['response'])
        
        st.divider()
    
    # Show chat input for questions
    st.subheader("💬 Ask Questions About the Indicators")
    st.info("""
    You can now ask questions about:
    - Specific indicators and their measurement methods
    - How to apply indicators to your project context
    - Clarifications about indicator definitions
    - Additional indicators that might be relevant
    """)
    
    # Display chat messages
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the indicators..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get response using query_knowledge_base() for follow-ups
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Use query_knowledge_base() for follow-up questions with timeout
                    response = query_knowledge_base(prompt, timeout=30)
                    
                    if 'output' in response and 'text' in response['output']:
                        response_text = response['output']['text']
                    else:
                        response_text = "I couldn't find relevant information in the Knowledge Base. Please try rephrasing your question."
                    
                    st.write(response_text)
                    
                    # Add assistant response
                    st.session_state.chat_messages.append({"role": "assistant", "content": response_text})
                
                except Exception as e:
                    error_message = str(e)
                    
                    # Provide user-friendly error messages
                    if "timed out" in error_message.lower():
                        error_msg = "⏱️ The query took too long. Please try a simpler question."
                    elif "not found" in error_message.lower():
                        error_msg = "❌ Knowledge Base connection issue. Please check your configuration."
                    elif "access denied" in error_message.lower():
                        error_msg = "🔒 Access denied. Please check your AWS credentials."
                    elif "throttl" in error_message.lower():
                        error_msg = "⏸️ Too many requests. Please wait a moment and try again."
                    else:
                        error_msg = f"❌ Error: {error_message}"
                    
                    st.error(error_msg)
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
    
    # Show export button
    st.divider()
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("📥 Export Summary", use_container_width=True, type="primary"):
            try:
                # Create export summary
                export_text = "# CBA Indicator Selection Summary\n\n"
                export_text += "## Project Information\n\n"
                
                for key, value in st.session_state.project_info.items():
                    if key != 'documents_uploaded' and value is not None and value != [] and value != '':
                        export_text += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
                
                export_text += "\n## Recommended Indicators\n\n"
                for idx, indicator_data in enumerate(st.session_state.indicators):
                    export_text += f"### Indicator Set {idx + 1}\n\n"
                    export_text += indicator_data['response'] + "\n\n"
                
                if st.session_state.chat_messages:
                    export_text += "\n## Discussion Summary\n\n"
                    for msg in st.session_state.chat_messages:
                        role = "User" if msg["role"] == "user" else "Assistant"
                        export_text += f"**{role}:** {msg['content']}\n\n"
                
                # Offer download
                st.download_button(
                    label="Download Summary",
                    data=export_text,
                    file_name=f"cba_indicator_summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
            
            except Exception as e:
                st.error(f"❌ Error creating export: {str(e)}")
                st.info("Please try again or contact support if the issue persists.")

if __name__ == "__main__":
    main()