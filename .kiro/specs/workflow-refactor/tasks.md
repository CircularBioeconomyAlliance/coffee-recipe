# Implementation Plan: Workflow Refactor

## Overview

This plan implements minimal workflow enforcement for the CBA Indicator Selection Assistant. The implementation adds a simple state machine to guide users through: upload → extract → ask → retrieve → chat, using direct boto3 for Knowledge Base access.

**Branch**: `feature/workflow-refactor`

## Tasks

- [x] 1. Create feature branch and set up workflow module
  - Create branch `feature/workflow-refactor` from main
  - Create `src/workflow.py` with imports and constants
  - Add S3_BUCKET constant: `cba-project-docs`
  - Add boto3 clients for bedrock-agent-runtime and s3
  - _Requirements: 1.1, 2.1, 5.1, 8.1_

- [x] 2. Implement core workflow helper functions
  - [x] 2.1 Implement `upload_document_to_s3(file_content, filename)` function
    - Upload to S3 with date-based key structure
    - Return S3 key for reference
    - _Requirements: 2.1, 2.3_
  
  - [x] 2.2 Implement `query_knowledge_base(query)` function
    - Use boto3 `retrieve_and_generate` API directly
    - No Strands memory abstraction
    - Return structured response
    - _Requirements: 5.1, 5.3, 8.1_
  
  - [x] 2.3 Implement `extract_project_info(text)` function
    - Use Strands Agent with use_llm tool
    - Extract: location, project_type, outcomes, budget, capacity
    - Return structured dict
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [x] 2.4 Implement `get_missing_fields(project_info)` function
    - Check required fields against project_info dict
    - Return list of missing field names
    - _Requirements: 4.1, 4.2_
  
  - [x] 2.5 Implement `is_info_complete(project_info)` function
    - Return True if all required fields present
    - Use get_missing_fields internally
    - _Requirements: 4.1, 4.5_

- [x] 3. Update app.py session state initialization
  - Add `workflow_phase` to session state (default: 'upload')
  - Add `project_info` dict to session state
  - Add `indicators` list to session state
  - Keep existing session management code
  - _Requirements: 1.3, 1.5, 9.1_

- [x] 4. Implement phase-based UI rendering in app.py
  - [x] 4.1 Add phase detection at start of main()
    - Get current phase from session state
    - Route to appropriate UI section
    - _Requirements: 1.1, 10.1_
  
  - [x] 4.2 Implement upload phase UI
    - Show file uploader prominently
    - Add "Skip to manual entry" button
    - On upload: extract text, transition to 'extract'
    - On skip: transition to 'ask'
    - _Requirements: 2.1, 10.3_
  
  - [x] 4.3 Implement extract phase UI
    - Show "Extracting information..." message
    - Call extract_project_info()
    - Update project_info in session state
    - Transition to 'ask' phase
    - _Requirements: 3.1, 3.4_
  
  - [x] 4.4 Implement ask phase UI
    - Display missing fields clearly
    - Show form for each missing field
    - On submit: update project_info
    - If complete: transition to 'retrieve'
    - If incomplete: stay in 'ask'
    - _Requirements: 4.2, 4.3, 4.4, 10.4_
  
  - [x] 4.5 Implement retrieve phase UI
    - Show "Retrieving indicators..." message
    - Build query from project_info
    - Call query_knowledge_base()
    - Store indicators in session state
    - Transition to 'chat' phase
    - _Requirements: 5.3, 5.5_
  
  - [x] 4.6 Implement chat phase UI
    - Display retrieved indicators
    - Show chat input for questions
    - Use query_knowledge_base() for follow-ups
    - Show export button
    - _Requirements: 6.2, 6.4, 10.5_

- [x] 5. Replace memory() tool calls with direct boto3
  - Find all `memory(action="retrieve", ...)` calls
  - Replace with `query_knowledge_base()` calls
  - Update response handling for new format
  - Remove memory from tools list
  - _Requirements: 5.1, 5.2, 8.1_

- [ ] 6. Add error handling
  - Add try/except around file operations
  - Add try/except around KB queries with timeout
  - Add try/except around extraction with fallback
  - Show user-friendly error messages
  - _Requirements: 2.5, 3.5, 8.4_

- [ ] 7. Checkpoint - Test workflow end-to-end
  - Test upload → extract → ask → retrieve → chat flow
  - Test skip upload → ask → retrieve → chat flow
  - Test error handling for each phase
  - Ensure all tests pass, ask the user if questions arise

- [ ] 8. Add simple unit tests
  - [ ] 8.1 Test get_missing_fields() function
    - Test with complete info
    - Test with partial info
    - Test with empty info
    - _Requirements: 4.1_
  
  - [ ] 8.2 Test is_info_complete() function
    - Test returns True when complete
    - Test returns False when incomplete
    - _Requirements: 4.1, 4.5_
  
  - [ ] 8.3 Test query_knowledge_base() function
    - Mock boto3 response
    - Verify correct API call structure
    - _Requirements: 5.1, 5.3_

- [x] 9. Update documentation
  - Update README.md with workflow description
  - Document S3 bucket requirement
  - _Requirements: N/A_

- [ ] 10. Final checkpoint and merge preparation
  - Run all tests
  - Test in Streamlit UI manually
  - Verify main branch unchanged
  - Prepare merge request
  - Ensure all tests pass, ask the user if questions arise

## Notes

- All work happens on `feature/workflow-refactor` branch
- Main branch remains stable during development
- Minimal changes to existing code (~150 lines total)
- No new classes or abstractions
- Direct boto3 for deterministic KB access
- S3 bucket: `cba-project-docs` for uploads