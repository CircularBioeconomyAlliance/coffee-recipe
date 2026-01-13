"""
Workflow helper functions for CBA Indicator Selection Assistant.

This module provides simple functions to support the workflow-driven approach:
- Document upload to S3
- Direct Knowledge Base queries via boto3
- Project information extraction
- Information completeness validation
"""

import boto3
import json
from datetime import datetime
from typing import Dict, List, Optional

from strands import Agent
from strands_tools import use_llm

from config import MODEL_ID, KNOWLEDGE_BASE_ID

# S3 bucket for document uploads
S3_BUCKET = 'cba-project-docs'

# AWS clients - direct boto3 usage for deterministic behavior
bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
s3_client = boto3.client('s3', region_name='us-west-2')

# Required fields for project information
REQUIRED_FIELDS = ['location', 'project_type', 'outcomes', 'budget', 'capacity']


def upload_document_to_s3(file_content: bytes, filename: str) -> str:
    """
    Upload document to S3 bucket with date-based key structure.
    
    Args:
        file_content: Binary content of the file
        filename: Original filename
        
    Returns:
        S3 key where the file was stored
        
    Raises:
        Exception: If upload fails with descriptive error message
        
    Requirements: 2.1, 2.3, 2.5
    """
    try:
        # Create date-based key structure: uploads/YYYYMMDD/filename
        date_prefix = datetime.now().strftime('%Y%m%d')
        key = f"uploads/{date_prefix}/{filename}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=file_content
        )
        
        return key
    
    except s3_client.exceptions.NoSuchBucket:
        raise Exception(f"S3 bucket '{S3_BUCKET}' does not exist. Please create the bucket first.")
    except s3_client.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        raise Exception(f"Failed to upload file to S3: {error_code} - {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error uploading file: {str(e)}")


def query_knowledge_base(query: str, timeout: int = 30) -> dict:
    """
    Query AWS Bedrock Knowledge Base directly using boto3 with timeout and retry.
    
    This replaces the Strands memory() tool for deterministic KB access.
    
    Args:
        query: Search query string
        timeout: Timeout in seconds (default: 30)
        
    Returns:
        Response dictionary from Bedrock API
        
    Raises:
        Exception: If query fails after retry with descriptive error message
        
    Requirements: 5.1, 5.3, 8.1, 8.4
    """
    import botocore.config
    
    # Configure client with timeout
    config = botocore.config.Config(
        read_timeout=timeout,
        connect_timeout=10,
        retries={'max_attempts': 2, 'mode': 'standard'}
    )
    
    # Create client with timeout config
    bedrock_client = boto3.client(
        'bedrock-agent-runtime',
        region_name='us-west-2',
        config=config
    )
    
    try:
        response = bedrock_client.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': f'arn:aws:bedrock:us-west-2::foundation-model/{MODEL_ID}'
                }
            }
        )
        
        return response
    
    except bedrock_client.exceptions.ResourceNotFoundException:
        raise Exception(f"Knowledge Base '{KNOWLEDGE_BASE_ID}' not found. Please verify the Knowledge Base ID.")
    except bedrock_client.exceptions.AccessDeniedException:
        raise Exception("Access denied to Bedrock Knowledge Base. Please check AWS credentials and permissions.")
    except bedrock_client.exceptions.ThrottlingException:
        raise Exception("Knowledge Base request was throttled. Please try again in a moment.")
    except botocore.exceptions.ReadTimeoutError:
        raise Exception(f"Knowledge Base query timed out after {timeout} seconds. Please try a simpler query.")
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        raise Exception(f"Knowledge Base query failed: {error_code} - {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error querying Knowledge Base: {str(e)}")


def extract_project_info(text: str) -> dict:
    """
    Extract structured project information from text using Strands Agent.
    Falls back to empty structure if extraction fails.
    
    Args:
        text: Document text to extract information from
        
    Returns:
        Dictionary with extracted fields: location, project_type, outcomes, budget, capacity
        Returns empty structure if extraction fails
        
    Requirements: 3.1, 3.2, 3.4, 3.5
    """
    extraction_prompt = """Extract the following project information from the provided text and return ONLY a valid JSON object:

Required fields:
- location: Geographic location (country, region, or coordinates)
- project_type: Type of project (e.g., "cotton farming", "agroforestry")
- outcomes: List of expected outcomes or goals
- budget: Budget level ("low", "medium", or "high")
- capacity: Technical capacity level ("basic", "intermediate", or "advanced")

Return format (JSON only, no other text):
{
    "location": "...",
    "project_type": "...",
    "outcomes": ["...", "..."],
    "budget": "...",
    "capacity": "..."
}

If a field cannot be determined from the text, use null for that field.

Text to analyze:
"""
    
    # Default empty structure for fallback
    empty_structure = {
        'location': None,
        'project_type': None,
        'outcomes': [],
        'budget': None,
        'capacity': None
    }
    
    try:
        agent = Agent(
            model=MODEL_ID,
            tools=[use_llm],
            system_prompt=extraction_prompt
        )
        
        result = agent(text)
        
        # Parse JSON from result
        try:
            # Try to find JSON in the response
            result_text = str(result)
            
            # Look for JSON object in the response
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                project_info = json.loads(json_str)
                
                # Validate structure - ensure all required fields exist
                for field in ['location', 'project_type', 'outcomes', 'budget', 'capacity']:
                    if field not in project_info:
                        project_info[field] = empty_structure[field]
                
                return project_info
            else:
                # No JSON found - return empty structure
                return empty_structure
                
        except (json.JSONDecodeError, ValueError) as e:
            # JSON parsing failed - return empty structure
            return empty_structure
    
    except Exception as e:
        # Agent execution failed - return empty structure
        # This allows the workflow to continue with manual entry
        return empty_structure


def get_missing_fields(project_info: dict) -> List[str]:
    """
    Check which required fields are missing from project_info.
    
    Args:
        project_info: Dictionary containing project information
        
    Returns:
        List of missing field names
        
    Requirements: 4.1, 4.2
    """
    missing = []
    
    for field in REQUIRED_FIELDS:
        value = project_info.get(field)
        
        # Check if field is missing or empty
        if value is None:
            missing.append(field)
        elif isinstance(value, list) and len(value) == 0:
            missing.append(field)
        elif isinstance(value, str) and value.strip() == '':
            missing.append(field)
    
    return missing


def is_info_complete(project_info: dict) -> bool:
    """
    Check if all required project information is present.
    
    Args:
        project_info: Dictionary containing project information
        
    Returns:
        True if all required fields are present, False otherwise
        
    Requirements: 4.1, 4.5
    """
    return len(get_missing_fields(project_info)) == 0
