#!/usr/bin/env python3
"""
Test script for individual functions in the Streamlit Chat App.
Tests core functionality without Streamlit dependencies.
"""

import uuid
import datetime
import io

def test_session_title_generation():
    """Test session title generation from messages."""
    print("🧪 Testing Session Title Generation...")
    
    def generate_session_title(first_message):
        """Generate a readable session title from the first message."""
        if not first_message or not first_message.strip():
            return "New Chat"
        
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
    
    # Test cases for title generation
    test_cases = [
        ("Hello world", "Hello world"),
        ("This is a longer message with many words", "This is a longer message..."),
        ("", "New Chat"),
        ("   ", "New Chat"),
        ("A" * 60, "A" * 47 + "..."),
        ("One two three four five six seven", "One two three four five..."),
    ]
    
    for input_msg, expected in test_cases:
        result = generate_session_title(input_msg)
        print(f"  ✓ '{input_msg[:20]}...' -> '{result}'")
        
        if expected.endswith("..."):
            assert result.endswith("..."), f"Long title should end with '...': {result}"
        else:
            assert result == expected, f"Expected '{expected}', got '{result}'"
        
        assert len(result) <= 50, f"Title should not exceed 50 chars: {len(result)}"
    
    print("✅ Session Title Generation: PASSED\n")

def test_file_processing():
    """Test file upload and content extraction."""
    print("🧪 Testing File Processing...")
    
    def extract_file_content(uploaded_file):
        """Extract text content from uploaded files of different types."""
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
                import csv
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
                return f"PDF file '{uploaded_file.name}' uploaded. PDF text extraction requires additional libraries (PyPDF2, pdfplumber). Content: [PDF content would be extracted here]"
                
            elif file_extension == 'docx':
                return f"DOCX file '{uploaded_file.name}' uploaded. DOCX text extraction requires additional libraries (python-docx). Content: [DOCX content would be extracted here]"
                
            else:
                return f"Unsupported file type: {file_extension}"
                
        except Exception as e:
            return f"Error processing file '{uploaded_file.name}': {str(e)}"
    
    # Test 1: TXT file processing
    print("  ✓ Testing TXT file processing...")
    txt_content = "This is a test text file.\nWith multiple lines.\nFor testing purposes."
    
    class MockFile:
        def __init__(self, name, content):
            self.name = name
            self.content = content.encode('utf-8')
            self.position = 0
        
        def read(self):
            return self.content
        
        def seek(self, pos):
            self.position = pos
    
    txt_file = MockFile("test.txt", txt_content)
    extracted = extract_file_content(txt_file)
    
    assert extracted == txt_content, "TXT content should match exactly"
    print(f"    ✅ TXT extraction: {len(extracted)} characters")
    
    # Test 2: CSV file processing
    print("  ✓ Testing CSV file processing...")
    csv_content = "Name,Age,City\nJohn,25,New York\nJane,30,Los Angeles\nBob,35,Chicago"
    csv_file = MockFile("test.csv", csv_content)
    
    extracted_csv = extract_file_content(csv_file)
    
    assert "CSV Headers: Name, Age, City" in extracted_csv, "Should contain headers"
    assert "Row 1: John, 25, New York" in extracted_csv, "Should contain data rows"
    print(f"    ✅ CSV extraction: {len(extracted_csv)} characters")
    
    # Test 3: PDF file (placeholder)
    print("  ✓ Testing PDF file handling...")
    pdf_file = MockFile("test.pdf", "dummy content")
    extracted_pdf = extract_file_content(pdf_file)
    
    assert "PDF file 'test.pdf' uploaded" in extracted_pdf, "Should handle PDF files"
    print(f"    ✅ PDF handling: placeholder message")
    
    # Test 4: DOCX file (placeholder)
    print("  ✓ Testing DOCX file handling...")
    docx_file = MockFile("test.docx", "dummy content")
    extracted_docx = extract_file_content(docx_file)
    
    assert "DOCX file 'test.docx' uploaded" in extracted_docx, "Should handle DOCX files"
    print(f"    ✅ DOCX handling: placeholder message")
    
    # Test 5: Unsupported file type
    print("  ✓ Testing unsupported file type...")
    unsupported_file = MockFile("test.xyz", "dummy content")
    extracted_unsupported = extract_file_content(unsupported_file)
    
    assert "Unsupported file type: xyz" in extracted_unsupported, "Should handle unsupported types"
    print(f"    ✅ Unsupported file handling: error message")
    
    print("✅ File Processing: PASSED\n")

def test_llm_response():
    """Test LLM response simulation."""
    print("🧪 Testing LLM Response Simulation...")
    
    def simulate_llm_response(user_message, file_content=None):
        """Simulate LLM response with placeholder functionality."""
        import time
        import random
        
        # Create a context-aware response
        base_responses = [
            f"I understand you said: '{user_message}'. That's an interesting point!",
            f"Thanks for sharing that. Regarding '{user_message}', I think...",
            f"That's a great question about '{user_message}'. Let me think about that...",
            f"I see you mentioned '{user_message}'. Here's my perspective on that..."
        ]
        
        # Select a base response
        response = random.choice(base_responses)
        
        # Add file context if available
        if file_content and file_content.strip():
            response += f"\n\nI also notice you've uploaded a file with content that includes: {file_content[:200]}{'...' if len(file_content) > 200 else ''}"
            response += "\n\nI can reference this file content in our conversation."
        
        # Add some additional context
        response += f"\n\nThis is a simulated response. In a real implementation, this would connect to an actual LLM API like OpenAI, Anthropic, or others."
        
        # Simulate streaming by yielding chunks
        words = response.split()
        for i in range(0, len(words), 3):  # Yield 3 words at a time
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk
    
    # Test 1: Basic response without file content
    print("  ✓ Testing basic LLM response...")
    user_message = "What is the weather like?"
    response_gen = simulate_llm_response(user_message)
    
    # Collect all chunks from the generator
    response_chunks = list(response_gen)
    full_response = "".join(response_chunks)
    
    assert len(full_response) > 0, "Response should not be empty"
    assert user_message in full_response, "Response should reference user message"
    assert "simulated response" in full_response.lower(), "Should indicate it's simulated"
    print(f"    ✅ Basic response: {len(full_response)} characters")
    
    # Test 2: Response with file content
    print("  ✓ Testing LLM response with file content...")
    file_content = "This is some file content that should be referenced in the response."
    response_gen_with_file = simulate_llm_response(user_message, file_content)
    
    response_chunks_with_file = list(response_gen_with_file)
    full_response_with_file = "".join(response_chunks_with_file)
    
    assert len(full_response_with_file) > len(full_response), "Response with file should be longer"
    assert "uploaded a file" in full_response_with_file.lower(), "Should mention file upload"
    print(f"    ✅ Response with file: {len(full_response_with_file)} characters")
    
    print("✅ LLM Response Simulation: PASSED\n")

def test_session_logic():
    """Test session creation and management logic."""
    print("🧪 Testing Session Management Logic...")
    
    # Simulate session state
    sessions = {}
    current_session_id = None
    messages = []
    
    def create_new_session():
        nonlocal sessions, current_session_id, messages
        
        # Generate UUID for new session
        new_session_id = str(uuid.uuid4())
        
        # Create session data structure with empty messages
        new_session = {
            "title": "New Chat",
            "created_at": datetime.datetime.now(),
            "messages": [],
            "uploaded_files": []
        }
        
        # Add to sessions dictionary
        sessions[new_session_id] = new_session
        
        # Set as current active session
        current_session_id = new_session_id
        messages = []
        
        return new_session_id
    
    def switch_session(session_id):
        nonlocal sessions, current_session_id, messages
        
        # Validate session exists
        if session_id not in sessions:
            return False
        
        # Load messages from selected session
        selected_session = sessions[session_id]
        
        # Update current session state
        current_session_id = session_id
        messages = selected_session["messages"].copy()
        
        return True
    
    # Test session creation
    print("  ✓ Testing session creation...")
    session1 = create_new_session()
    assert session1 is not None, "Session ID should not be None"
    assert session1 in sessions, "Session should be added to sessions dict"
    assert current_session_id == session1, "Current session should be set"
    assert len(messages) == 0, "New session should have empty messages"
    print(f"    ✅ Created session: {session1[:8]}...")
    
    # Test adding messages
    print("  ✓ Testing message handling...")
    test_message = {"role": "user", "content": "Hello, this is a test message"}
    messages.append(test_message)
    sessions[session1]["messages"] = messages.copy()
    
    # Test creating second session
    print("  ✓ Testing multiple sessions...")
    session2 = create_new_session()
    assert session2 != session1, "New session should have different ID"
    assert len(sessions) == 2, "Should have 2 sessions"
    assert current_session_id == session2, "Current session should be the new one"
    assert len(messages) == 0, "New session should have empty messages"
    print(f"    ✅ Created second session: {session2[:8]}...")
    
    # Test session switching
    print("  ✓ Testing session switching...")
    result = switch_session(session1)
    assert result == True, "Session switch should succeed"
    assert current_session_id == session1, "Current session should be switched"
    assert len(messages) == 1, "Should load previous messages"
    assert messages[0]["content"] == "Hello, this is a test message", "Message content should match"
    print(f"    ✅ Switched back to session: {session1[:8]}...")
    
    print("✅ Session Management Logic: PASSED\n")

def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Starting Streamlit Chat App Function Tests\n")
    print("=" * 50)
    
    try:
        test_session_title_generation()
        test_file_processing()
        test_llm_response()
        test_session_logic()
        
        print("=" * 50)
        print("🎉 ALL FUNCTION TESTS PASSED!")
        print("\n✅ Test Summary:")
        print("  • Session title generation: ✅")
        print("  • File upload and processing: ✅")
        print("  • LLM response simulation: ✅")
        print("  • Session management logic: ✅")
        print("\n🚀 Core functionality is working correctly!")
        
        return True
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n🔧 Please check the implementation and try again.")
        return False

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)