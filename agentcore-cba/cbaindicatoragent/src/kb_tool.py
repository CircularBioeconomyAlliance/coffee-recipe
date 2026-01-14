"""Knowledge Base retrieval tool for CBA Indicator Selection"""
import os
import boto3
from strands import tool

KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID", "0ZQBMXEKDI")
REGION = os.getenv("AWS_REGION", "us-west-2")

# Initialize bedrock-agent-runtime client
bedrock_agent_runtime = boto3.client(
    'bedrock-agent-runtime',
    region_name=REGION
)

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
    try:
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': max_results
                }
            }
        )
        
        # Format the results
        results = []
        for idx, result in enumerate(response.get('retrievalResults', []), 1):
            content = result.get('content', {}).get('text', '')
            score = result.get('score', 0)
            
            # Get metadata if available
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            
            results.append(f"""
Result {idx} (Relevance: {score:.2f}):
Source: {source}
Content: {content}
---
""")
        
        if not results:
            return "No relevant indicators or methods found for this query."
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"


@tool
def search_indicators_by_outcome(outcome: str) -> str:
    """
    Search for indicators specifically aligned with a desired project outcome.
    
    Args:
        outcome: The desired project outcome (e.g., "reduce waste", "increase income")
    
    Returns:
        Indicators that measure progress toward this outcome
    """
    query = f"indicators that measure {outcome} in circular bioeconomy projects"
    return search_cba_indicators(query, max_results=5)


@tool
def search_methods_by_budget(budget_range: str, commodity: str = "") -> str:
    """
    Search for measurement methods appropriate for a given budget range.
    
    Args:
        budget_range: Budget range (e.g., "low", "medium", "high", "$0-10k", "$10k-50k")
        commodity: Optional commodity/product type to filter methods
    
    Returns:
        Methods that fit within the specified budget
    """
    commodity_filter = f"for {commodity} " if commodity else ""
    query = f"measurement methods {commodity_filter}with {budget_range} budget cost-effective affordable"
    return search_cba_indicators(query, max_results=5)


@tool
def search_location_specific_indicators(location: str, commodity: str = "") -> str:
    """
    Search for indicators and considerations specific to a geographic location.
    
    Args:
        location: Geographic location or region
        commodity: Optional commodity/product type
    
    Returns:
        Location-specific indicators and implementation considerations
    """
    commodity_filter = f"{commodity} " if commodity else ""
    query = f"{commodity_filter}indicators and methods for {location} region location-specific considerations"
    return search_cba_indicators(query, max_results=5)
