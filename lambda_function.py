import json
import boto3
import uuid
import base64
import os
import io
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# PDF extraction - pypdf must be included in Lambda layer
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    logger.warning("pypdf not available - PDF text extraction disabled")
    PDF_SUPPORT = False

# Get configuration from environment variables (with fallbacks for local dev)
AGENT_ARN = os.environ.get('BEDROCK_AGENTCORE_ARN', 'arn:aws:bedrock-agentcore:us-west-2:687995992314:runtime/cbaindicatoragent_Agent-buoE288RIT')
UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET_NAME', 'cba-indicator-uploads')
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')

agentcore = boto3.client('bedrock-agentcore', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)

# In-memory store for recommendations (in production, use DynamoDB)
recommendations_store = {}

def lambda_handler(event, context):
    path = event.get('rawPath', event.get('path', ''))
    method = event.get('requestContext', {}).get('http', {}).get('method', 'POST')
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return cors_response()
    
    # Route to appropriate handler (handle both /chat and /prod/chat)
    if '/chat' in path:
        return handle_chat(event)
    elif '/upload' in path:
        return handle_upload(event)
    elif '/recommendations' in path:
        return handle_recommendations(event)
    else:
        return {
            'statusCode': 404,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Not found'})
        }

def cors_headers():
    """Return standard CORS headers."""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

def cors_response():
    """Return CORS preflight response."""
    return {
        'statusCode': 200,
        'headers': cors_headers(),
        'body': ''
    }

def error_response(message, status_code=400):
    """Return standardized error response."""
    return {
        'statusCode': status_code,
        'headers': cors_headers(),
        'body': json.dumps({'error': message})
    }

def handle_chat(event):
    try:
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '')
        session_id = body.get('session_id') or str(uuid.uuid4())
        
        # Input validation
        if not message or not message.strip():
            return error_response("Message is required", 400)
        if len(message) > 10000:
            return error_response("Message too long. Maximum 10000 characters.", 400)
        
        payload = json.dumps({"prompt": message}).encode()
        
        response = agentcore.invoke_agent_runtime(
            agentRuntimeArn=AGENT_ARN,
            runtimeSessionId=session_id,
            payload=payload,
            qualifier="DEFAULT"
        )
        
        content = []
        for chunk in response.get("response", []):
            decoded = chunk.decode('utf-8')
            for line in decoded.split('\n'):
                line = line.strip()
                if line.startswith('data: '):
                    text = line[6:].strip().strip('"')
                    if text:
                        content.append(text)
        
        # Join and clean up formatting
        response_text = ''.join(content)
        response_text = response_text.replace('\\n', '\n')  # Fix escaped newlines
        
        # Try to extract indicator recommendations from the response
        indicators = extract_indicators_from_response(response_text)
        if indicators:
            # Store recommendations for this session
            recommendations_store[session_id] = {
                'indicators': indicators,
                'timestamp': str(uuid.uuid1())  # For TTL tracking
            }
            logger.info(f"Stored {len(indicators)} indicators for session {session_id}")
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'response': response_text,
                'session_id': session_id,
                'has_recommendations': len(indicators) > 0
            })
        }
    except Exception as e:
        logger.error(f"Chat handler error: {e}")
        return error_response(f"Chat processing failed: {str(e)}", 500)

def handle_upload(event):
    try:
        # Get base64 encoded file
        body = event.get('body', '')
        is_base64 = event.get('isBase64Encoded', False)
        
        if not body:
            return error_response("No file content provided", 400)
        
        if isinstance(body, str):
            if is_base64:
                file_bytes = base64.b64decode(body)
            else:
                # Some API Gateway configs pass base64 but don't set isBase64Encoded
                try:
                    file_bytes = base64.b64decode(body, validate=True)
                except Exception:
                    file_bytes = body.encode()
        else:
            file_bytes = body
        
        # Validate file size (max 10MB)
        if len(file_bytes) > 10 * 1024 * 1024:
            return error_response("File too large. Maximum size is 10MB.", 413)
        
        # Upload to S3
        file_key = f"uploads/{uuid.uuid4()}.pdf"
        s3.put_object(Bucket=UPLOAD_BUCKET, Key=file_key, Body=file_bytes)
        s3_uri = f"s3://{UPLOAD_BUCKET}/{file_key}"
        logger.info(f"File uploaded to {s3_uri}")
        
        # Extract text from PDF
        document_text = ""
        if PDF_SUPPORT:
            try:
                reader = PdfReader(io.BytesIO(file_bytes))
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                document_text = "\n".join(text_parts)
                logger.info(f"Extracted {len(document_text)} characters from PDF")
            except Exception as pdf_error:
                logger.error(f"PDF extraction failed: {pdf_error}")
                return error_response(f"Could not read PDF file: {str(pdf_error)}", 422)
        else:
            return error_response("PDF processing not available. Please contact support.", 503)
        
        if not document_text.strip():
            return error_response("PDF appears to be empty or contains no extractable text.", 422)
        
        # Use Claude to analyze the document content (truncate to avoid token limits)
        truncated_text = document_text[:15000]  # ~4k tokens
        prompt = """Analyze this project document and extract:
1. Location/Region
2. Primary Commodity/Product
3. Budget Range

Return ONLY a JSON object with these fields: {"location": "...", "commodity": "...", "budget": "..."}
If a field cannot be determined, use null for that field."""
        
        response = bedrock_runtime.invoke_model(
            modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [{
                    "role": "user",
                    "content": f"{prompt}\n\nDocument content:\n{truncated_text}"
                }]
            })
        )
        
        result = json.loads(response['body'].read())
        extracted = result['content'][0]['text']
        
        # Try to parse JSON - handle markdown code blocks
        extracted_clean = extracted.strip()
        if extracted_clean.startswith('```'):
            # Remove markdown code block
            lines = extracted_clean.split('\n')
            extracted_clean = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])
        
        try:
            data = json.loads(extracted_clean)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}\nResponse: {extracted}")
            return error_response("Could not extract project information from document. Please ensure it contains location, commodity, and budget details.", 422)
        
        # Format response to match frontend expectations
        found = {}
        missing = []
        
        if data.get('location'):
            found['location'] = data['location']
        else:
            missing.append('Project Location')
            
        if data.get('commodity'):
            found['commodity'] = data['commodity']
        else:
            missing.append('Primary Commodity')
            
        if data.get('budget'):
            found['budget'] = data['budget']
        else:
            missing.append('Budget Range')
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'found': found, 'missing': missing, 's3_uri': s3_uri})
        }
    except Exception as e:
        logger.error(f"Upload handler error: {e}")
        return error_response(f"Upload processing failed: {str(e)}", 500)

def extract_indicators_from_response(response_text):
    """
    Extract structured indicator data from agent response.
    Parses the formatted output to create indicator objects.
    """
    indicators = []
    
    # Look for indicator blocks in the response
    # Format: INDICATOR #X with ID, Name, Definition, Method, Attributes
    import re
    
    # Pattern to match indicator blocks
    indicator_pattern = r'INDICATOR #(\d+).*?ID:\s*([^\n]+).*?Name:\s*([^\n]+).*?(?:Full Definition|Definition):\s*([^\n]+(?:\n(?!Recommended|Why|Attributes|Mapping|DOI)[^\n]+)*)'
    
    matches = re.findall(indicator_pattern, response_text, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        try:
            indicator = {
                'id': int(match[1].strip()) if match[1].strip().isdigit() else hash(match[1].strip()) % 1000,
                'name': match[2].strip(),
                'definition': match[3].strip()[:500],  # Truncate long definitions
                'component': 'Unknown',  # Could be parsed if present
                'class': 'Unknown',
                'cost': 'Medium',
                'accuracy': 'Medium',
                'ease': 'Medium',
                'principle': '',
                'criterion': '',
                'priority': 'Primary',
                'methods': []
            }
            
            # Try to extract attributes if present
            attr_match = re.search(r'Accuracy:\s*(\w+)', response_text[response_text.find(match[2]):])
            if attr_match:
                indicator['accuracy'] = attr_match.group(1)
            
            cost_match = re.search(r'Cost:\s*(\w+)', response_text[response_text.find(match[2]):])
            if cost_match:
                indicator['cost'] = cost_match.group(1)
            
            ease_match = re.search(r'Ease[^:]*:\s*(\w+)', response_text[response_text.find(match[2]):])
            if ease_match:
                indicator['ease'] = ease_match.group(1)
            
            indicators.append(indicator)
        except Exception as e:
            logger.warning(f"Failed to parse indicator: {e}")
            continue
    
    return indicators

def handle_recommendations(event):
    """
    Handle GET /recommendations?session_id=xxx
    Returns stored indicator recommendations for a session.
    """
    try:
        # Get session_id from query parameters
        params = event.get('queryStringParameters', {}) or {}
        session_id = params.get('session_id')
        
        if not session_id:
            return error_response("session_id query parameter is required", 400)
        
        # Look up recommendations for this session
        session_data = recommendations_store.get(session_id)
        
        if not session_data:
            # Return empty array if no recommendations found
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({
                    'indicators': [],
                    'message': 'No recommendations found for this session. Please complete the chat conversation first.'
                })
            }
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'indicators': session_data['indicators'],
                'session_id': session_id
            })
        }
    except Exception as e:
        logger.error(f"Recommendations handler error: {e}")
        return error_response(f"Failed to retrieve recommendations: {str(e)}", 500)
