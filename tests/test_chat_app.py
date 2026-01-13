#!/usr/bin/env python3
"""
Test script for Streamlit Chat App functionality.
Tests session creation, switching, file upload, and message persistence.
"""

import sys
import os
import uuid
import datetime
import io
import tempfile

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions from our chat app
from src.app import (
    create_new_session,
    switch_session,
    generate_session_title,
    extract_file_content,
)

class MockSessionState:
    """Mock Streamlit session state for testing."""
    def __init__(self):
        self.sessions = {}
        self.current_session_id = None
        self.messages = []
        self.uploaded_file = None
        self.file_content = None

def test_session_creation():
    """Test session creation and switching functionality."""
    print("Testing Session Creation and Switching...")

    # Mock streamlit session state
    from src import app
    mock_st = MockSessionState()
    app.st.session_state = mock_st

    # Test 1: Create new session
    print("  - Testing session creation...")
    session_id = create_new_session()

    assert session_id is not None, "Session ID should not be None"
    assert session_id in mock_st.sessions, "Session should be added to sessions dict"
    assert mock_st.current_session_id == session_id, "Current session should be set"
    assert len(mock_st.messages) == 0, "New session should have empty messages"
    print(f"    Created session: {session_id[:8]}...")

    # Test 2: Add a message to current session
    test_message = {"role": "user", "content": "Hello, this is a test message"}
    mock_st.messages.append(test_message)
    mock_st.sessions[session_id]["messages"] = mock_st.messages.copy()

    # Test 3: Create another session
    print("  - Testing multiple sessions...")
    session_id_2 = create_new_session()

    assert session_id_2 != session_id, "New session should have different ID"
    assert len(mock_st.sessions) == 2, "Should have 2 sessions"
    assert mock_st.current_session_id == session_id_2, "Current session should be the new one"
    assert len(mock_st.messages) == 0, "New session should have empty messages"
    print(f"    Created second session: {session_id_2[:8]}...")

    # Test 4: Switch back to first session
    print("  - Testing session switching...")
    result = switch_session(session_id)

    assert result == True, "Session switch should succeed"
    assert mock_st.current_session_id == session_id, "Current session should be switched"
    assert len(mock_st.messages) == 1, "Should load previous messages"
    assert mock_st.messages[0]["content"] == "Hello, this is a test message", "Message content should match"
    print(f"    Switched back to session: {session_id[:8]}...")

    # Test 5: Test invalid session switch
    print("  - Testing invalid session handling...")
    invalid_result = switch_session("invalid-session-id")
    assert invalid_result == False, "Invalid session switch should fail"

    print("PASSED: Session Creation and Switching\n")

def test_session_title_generation():
    """Test session title generation from messages."""
    print("Testing Session Title Generation...")

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
        print(f"  - '{input_msg[:20]}...' -> '{result}'")

        if expected.endswith("..."):
            assert result.endswith("..."), f"Long title should end with '...': {result}"
        else:
            assert result == expected, f"Expected '{expected}', got '{result}'"

        assert len(result) <= 50, f"Title should not exceed 50 chars: {len(result)}"

    print("PASSED: Session Title Generation\n")

def test_file_processing():
    """Test file upload and content extraction."""
    print("Testing File Processing...")

    # Test 1: TXT file processing
    print("  - Testing TXT file processing...")
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
    print(f"    TXT extraction: {len(extracted)} characters")

    # Test 2: CSV file processing
    print("  - Testing CSV file processing...")
    csv_content = "Name,Age,City\nJohn,25,New York\nJane,30,Los Angeles\nBob,35,Chicago"
    csv_file = MockFile("test.csv", csv_content)

    extracted_csv = extract_file_content(csv_file)

    assert "CSV Headers: Name, Age, City" in extracted_csv, "Should contain headers"
    assert "Row 1: John, 25, New York" in extracted_csv, "Should contain data rows"
    print(f"    CSV extraction: {len(extracted_csv)} characters")

    # Test 3: PDF file (placeholder)
    print("  - Testing PDF file handling...")
    pdf_file = MockFile("test.pdf", "dummy content")
    extracted_pdf = extract_file_content(pdf_file)

    assert "PDF file 'test.pdf' uploaded" in extracted_pdf, "Should handle PDF files"
    print(f"    PDF handling: placeholder message")

    # Test 4: DOCX file (placeholder)
    print("  - Testing DOCX file handling...")
    docx_file = MockFile("test.docx", "dummy content")
    extracted_docx = extract_file_content(docx_file)

    assert "DOCX file 'test.docx' uploaded" in extracted_docx, "Should handle DOCX files"
    print(f"    DOCX handling: placeholder message")

    # Test 5: Unsupported file type
    print("  - Testing unsupported file type...")
    unsupported_file = MockFile("test.xyz", "dummy content")
    extracted_unsupported = extract_file_content(unsupported_file)

    assert "Unsupported file type: xyz" in extracted_unsupported, "Should handle unsupported types"
    print(f"    Unsupported file handling: error message")

    print("PASSED: File Processing\n")

def test_message_persistence():
    """Test that messages persist correctly across sessions."""
    print("Testing Message Persistence...")

    # Mock streamlit session state
    from src import app
    mock_st = MockSessionState()
    app.st.session_state = mock_st

    # Create first session and add messages
    print("  - Testing message persistence across sessions...")
    session1 = create_new_session()

    # Add messages to session 1
    messages_session1 = [
        {"role": "user", "content": "Hello from session 1"},
        {"role": "assistant", "content": "Hi there! This is session 1 response."}
    ]
    mock_st.messages = messages_session1.copy()
    mock_st.sessions[session1]["messages"] = messages_session1.copy()

    # Create second session and add different messages
    session2 = create_new_session()
    messages_session2 = [
        {"role": "user", "content": "Hello from session 2"},
        {"role": "assistant", "content": "Hi! This is session 2 response."}
    ]
    mock_st.messages = messages_session2.copy()
    mock_st.sessions[session2]["messages"] = messages_session2.copy()

    # Switch back to session 1 and verify messages
    switch_session(session1)
    assert len(mock_st.messages) == 2, "Session 1 should have 2 messages"
    assert mock_st.messages[0]["content"] == "Hello from session 1", "First message should match"
    assert mock_st.messages[1]["content"] == "Hi there! This is session 1 response.", "Second message should match"
    print(f"    Session 1 messages preserved: {len(mock_st.messages)} messages")

    # Switch to session 2 and verify messages
    switch_session(session2)
    assert len(mock_st.messages) == 2, "Session 2 should have 2 messages"
    assert mock_st.messages[0]["content"] == "Hello from session 2", "First message should match"
    assert mock_st.messages[1]["content"] == "Hi! This is session 2 response.", "Second message should match"
    print(f"    Session 2 messages preserved: {len(mock_st.messages)} messages")

    print("PASSED: Message Persistence\n")

def run_all_tests():
    """Run all tests and report results."""
    print("Starting Streamlit Chat App Tests\n")
    print("=" * 50)

    try:
        test_session_creation()
        test_session_title_generation()
        test_file_processing()
        test_message_persistence()

        print("=" * 50)
        print("ALL TESTS PASSED!")
        print("\nTest Summary:")
        print("  - Session creation and switching: PASSED")
        print("  - Session title generation: PASSED")
        print("  - File upload and processing: PASSED")
        print("  - Message persistence: PASSED")
        print("\nNote: Agent response tests skipped (requires AWS credentials)")

        return True

    except Exception as e:
        print("=" * 50)
        print(f"TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nPlease check the implementation and try again.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
