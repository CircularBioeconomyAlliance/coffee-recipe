import os
import sys
from pathlib import Path

# Add src directory to path for imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from strands import Agent, tool
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# Import MCP client
try:
    from mcp_client.client import get_streamable_http_mcp_client
except ImportError:
    from contextlib import nullcontext
    from types import SimpleNamespace
    def get_streamable_http_mcp_client():
        return nullcontext(SimpleNamespace(list_tools_sync=lambda: []))

# Import model loader
try:
    from model.load import load_model
except ImportError:
    from strands.models import BedrockModel
    def load_model():
        return BedrockModel(model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0")

# Import KB tools
try:
    from kb_tool import (
        search_cba_indicators,
        search_indicators_by_outcome,
        search_methods_by_budget,
        search_location_specific_indicators
    )
except ImportError:
    # Define stub tools if import fails
    @tool
    def search_cba_indicators(query: str, max_results: int = 10) -> str:
        return "KB tool not available"
    @tool
    def search_indicators_by_outcome(outcome: str) -> str:
        return "KB tool not available"
    @tool
    def search_methods_by_budget(budget_range: str, commodity: str = "") -> str:
        return "KB tool not available"
    @tool
    def search_location_specific_indicators(location: str, commodity: str = "") -> str:
        return "KB tool not available"

MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
REGION = os.getenv("AWS_REGION", "us-west-2")
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID", "0ZQBMXEKDI")

# Skip MCP client for now (no Gateway configured)
from contextlib import nullcontext
from types import SimpleNamespace
strands_mcp_client = nullcontext(SimpleNamespace(list_tools_sync=lambda: []))

# CBA Project Profile State
project_profile = {
    "location": None,
    "commodity": None,
    "budget": None,
    "outcomes": None,
    "capacity": None
}

@tool
def set_project_location(location: str) -> str:
    """Set the project location/region"""
    project_profile["location"] = location
    return f"Location set to: {location}"

@tool
def set_project_commodity(commodity: str) -> str:
    """Set the primary commodity/product"""
    project_profile["commodity"] = commodity
    return f"Commodity set to: {commodity}"

@tool
def set_project_budget(budget: str) -> str:
    """Set the project budget range"""
    project_profile["budget"] = budget
    return f"Budget set to: {budget}"

@tool
def set_project_outcomes(outcomes: str) -> str:
    """Set the desired project outcomes"""
    project_profile["outcomes"] = outcomes
    return f"Outcomes set to: {outcomes}"

@tool
def set_technical_capacity(capacity: str) -> str:
    """Set the technical capacity level (optional)"""
    project_profile["capacity"] = capacity
    return f"Technical capacity set to: {capacity}"

@tool
def get_project_profile() -> dict:
    """Get the current project profile"""
    return project_profile

# Integrate with Bedrock AgentCore
app = BedrockAgentCoreApp()
log = app.logger

@app.entrypoint
async def invoke(payload, context):
    session_id = getattr(context, 'session_id', 'default')

    # Configure memory if available
    session_manager = None
    if MEMORY_ID:
        session_manager = AgentCoreMemorySessionManager(
            AgentCoreMemoryConfig(
                memory_id=MEMORY_ID,
                session_id=session_id,
                actor_id="cba-user",
                retrieval_config={
                    "/users/cba-user/profile": RetrievalConfig(top_k=5, relevance_score=0.5),
                }
            ),
            REGION
        )
    else:
        log.warning("MEMORY_ID is not set. Skipping memory session manager initialization.")

    with strands_mcp_client as client:
        # Get MCP Tools
        tools = client.list_tools_sync()

        # Create agent with Knowledge Base
        agent = Agent(
            model=load_model(),
            session_manager=session_manager,
            system_prompt=f"""
You are the CBA (Circular Bioeconomy Alliance) Indicator Selection Assistant. Your role is to help users identify the most relevant monitoring and evaluation indicators for their circular bioeconomy projects.

You have access to a knowledge base containing 801 methods and 224 indicators from the CBA M&E framework (Knowledge Base ID: {KNOWLEDGE_BASE_ID}).

Your workflow:
1. Gather project profile information through conversation:
   - Location/Region (required)
   - Primary Commodity/Product (required)
   - Budget Range (required)
   - Desired Outcomes (required)
   - Technical Capacity (optional - for filtering method complexity)

2. Use the provided tools to:
   - Store profile information as you collect it (set_project_* tools)
   - Search the knowledge base for relevant indicators (search_cba_indicators)
   - Find indicators aligned with outcomes (search_indicators_by_outcome)
   - Identify budget-appropriate methods (search_methods_by_budget)
   - Get location-specific considerations (search_location_specific_indicators)

3. Once you have the required information, use the KB search tools to recommend:
   - Relevant indicators aligned with their outcomes
   - Appropriate methods based on their budget and capacity
   - Location-specific considerations

4. Present recommendations clearly with:
   - Indicator names and descriptions
   - Why each is relevant to their project
   - Implementation considerations
   - Budget and capacity requirements

Be conversational, ask one question at a time, and confirm understanding before moving forward. After gathering all required information, actively search the knowledge base to provide specific, actionable recommendations.
            """,
            tools=[
                set_project_location,
                set_project_commodity,
                set_project_budget,
                set_project_outcomes,
                set_technical_capacity,
                get_project_profile,
                search_cba_indicators,
                search_indicators_by_outcome,
                search_methods_by_budget,
                search_location_specific_indicators
            ] + tools
        )

        # Execute and format response
        stream = agent.stream_async(payload.get("prompt"))

        async for event in stream:
            # Handle Text parts of the response
            if "data" in event and isinstance(event["data"], str):
                yield event["data"]

def format_response(result) -> str:
    """Format the agent response"""
    return str(result)

if __name__ == "__main__":
    app.run()