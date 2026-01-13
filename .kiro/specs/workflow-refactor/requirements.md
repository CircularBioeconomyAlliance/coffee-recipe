# Requirements Document

## Introduction

This specification defines the refactoring of the existing CBA (Circular Bioeconomy alliance) Indicator Selection Assistant from a free-form chatbot into a deterministic, state-driven workflow system. The refactored system will enforce a structured decision-support process with explicit state transitions, treating the system as a workflow orchestrator with a chat layer rather than a conversational AI.

## Glossary

- **Orchestrator**: The central state management component that controls workflow progression
- **ProjectState**: Structured data object containing all extracted project information
- **State_Transition**: Movement from one workflow phase to another based on completion criteria
- **Knowledge_Base**: AWS Bedrock Knowledge Base containing indicator data
- **Workflow_Phase**: Distinct stages in the indicator selection process
- **Intent_Classifier**: Component that categorizes user messages in chat mode
- **Document_Processor**: Component that extracts structured data from uploaded files
- **Export_Generator**: Component that creates downloadable summary documents

## Requirements

### Requirement 1: State-Driven Orchestration

**User Story:** As a system administrator, I want the application to follow a deterministic workflow, so that user interactions are predictable and governed.

#### Acceptance Criteria

1. THE Orchestrator SHALL enforce a sequential workflow with six distinct phases: INIT, DOCUMENT_INTAKE, EXTRACTION, COMPLETENESS_CHECK, INDICATOR_RETRIEVAL, CONSTRAINED_CHAT
2. WHEN a user attempts to skip a workflow phase, THE Orchestrator SHALL prevent progression and redirect to the current required phase
3. THE Orchestrator SHALL maintain ProjectState throughout the entire workflow session
4. WHEN a workflow phase is completed, THE Orchestrator SHALL automatically transition to the next phase
5. THE Orchestrator SHALL persist the current workflow phase in session state

### Requirement 2: Document Processing and Storage

**User Story:** As a user, I want to upload project documents, so that the system can extract relevant information for indicator selection.

#### Acceptance Criteria

1. WHEN a user uploads documents in supported formats (PDF, Excel, CSV, TXT) via the streamlit infterface, THE Document_Processor SHALL store them in S3 (use placeholder bucket for now)
2. THE Document_Processor SHALL support PDF text extraction, Excel data extraction, CSV parsing, and plain text processing
3. WHEN documents are successfully uploaded, THE Orchestrator SHALL mark documents_present as true in ProjectState
4. WHEN no documents are uploaded, THE Orchestrator SHALL mark documents_present as false and skip extraction
5. THE Document_Processor SHALL handle file processing errors gracefully and provide user feedback

### Requirement 3: Structured Information Extraction

**User Story:** As a system, I want to extract key project information from documents, so that I can make informed indicator recommendations.

#### Acceptance Criteria

1. WHEN documents_present is true, THE Document_Processor SHALL extract predefined fields: outcomes, location, commodity, budget, capacity, area of land, community information and impact
2. THE Document_Processor SHALL output extracted information as structured JSON
3. THE Document_Processor SHALL use LLM capabilities strictly for extraction, not reasoning or recommendations
4. WHEN extraction is complete, THE Orchestrator SHALL populate ProjectState with extracted fields
5. THE Document_Processor SHALL handle cases where documents contain incomplete information

### Requirement 4: Information Completeness Validation

**User Story:** As a system, I want to ensure all required project information is available, so that indicator recommendations are comprehensive.

#### Acceptance Criteria

1. THE Orchestrator SHALL validate ProjectState against REQUIRED_FIELDS: outcomes, location, commodity, budget, capacity, area of land, community information and impact
2. WHEN required fields are missing, THE Orchestrator SHALL request only the missing fields from the user
3. WHEN the user provides missing information, THE Orchestrator SHALL merge responses into ProjectState
4. THE Orchestrator SHALL repeat completeness checks until all required fields are populated
5. WHEN ProjectState is complete, THE Orchestrator SHALL mark it as COMPLETE and proceed to indicator retrieval

### Requirement 5: Deterministic Indicator Retrieval

**User Story:** As a user, I want to receive relevant indicator recommendations based on my project information, so that I can make informed measurement decisions.

#### Acceptance Criteria

1. WHEN ProjectState is COMPLETE, THE Orchestrator SHALL query AWS Bedrock Knowledge Base using the SDK directly, using simple code
2. THE Orchestrator SHALL NOT use Strands memory abstraction for Knowledge Base queries
3. THE Orchestrator SHALL build deterministic queries from ProjectState fields only
4. THE Orchestrator SHALL NOT infer or fabricate indicators beyond Knowledge Base content
5. WHEN indicators are retrieved, THE Orchestrator SHALL store them as read-only state and transition to constrained chat mode

### Requirement 6: Chat Mode

**User Story:** As a user, I want to ask questions about recommended indicators, so that I can understand their applicability and measurement methods.

#### Acceptance Criteria

1. THE Intent_Classifier SHALL categorize each user message as within-scope or out-of-scope
2. WHEN user intent is within allowed scope (indicators, methods, applicability, clarifications, CBA, farming, follow up, QnA on the indicators), THE Orchestrator SHALL provide responses using retrieved indicator data
3. WHEN user intent is out-of-scope, THE Orchestrator SHALL politely refuse and restate allowed topics
4. THE Orchestrator SHALL allow additional Bedrock Knowledge Base queries for relevant follow-up questions
5. THE Orchestrator SHALL NOT introduce new indicators unless explicitly requested by the user

### Requirement 7: Export and Summary Generation

**User Story:** As a user, I want to download a summary of my indicator selection process, so that I can reference it for project implementation.

#### Acceptance Criteria

1. THE Export_Generator SHALL be available only after indicator retrieval is complete
2. WHEN export is requested, THE Export_Generator SHALL create a document containing ProjectState summary, selected indicators with measurement methods, rationale for each indicator, and concise chat interaction summary
3. THE Export_Generator SHALL NOT introduce new information during export generation
4. THE Export_Generator SHALL support downloadable document formats (PDF, Word, or structured text) on the streamlit interface

### Requirement 8: AWS Bedrock Integration

**User Story:** As a system, I want to use AWS Bedrock Knowledge Base directly, so that indicator data access is deterministic and reliable.

#### Acceptance Criteria

1. THE Orchestrator SHALL use AWS Bedrock SDK for all Knowledge Base interactions
2. THE Orchestrator SHALL NOT use Strands memory tool for Knowledge Base access
3. WHEN querying the Knowledge Base, THE Orchestrator SHALL use structured queries based on ProjectState
4. THE Orchestrator SHALL handle Bedrock API errors gracefully and provide user feedback
5. THE Orchestrator SHALL maintain existing Knowledge Base ID and region configuration

### Requirement 10: User Interface Adaptation

**User Story:** As a user, I want the interface to clearly indicate my current workflow phase, so that I understand what actions are available.

#### Acceptance Criteria

1. THE User_Interface SHALL display the current workflow phase prominently
2. THE User_Interface SHALL show progress indicators for completed and remaining phases
3. WHEN in document upload phase, THE User_Interface SHALL emphasize file upload functionality
4. WHEN in information gathering phase, THE User_Interface SHALL present structured forms for missing fields
5. WHEN in constrained chat mode, THE User_Interface SHALL display allowed topic guidelines