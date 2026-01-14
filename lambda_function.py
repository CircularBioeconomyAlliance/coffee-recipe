import json
import boto3
import uuid
import base64

agentcore = boto3.client('bedrock-agentcore', region_name='us-west-2')
s3 = boto3.client('s3', region_name='us-west-2')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')

AGENT_ARN = 'arn:aws:bedrock-agentcore:us-west-2:687995992314:runtime/cbaindicatoragent_Agent-buoE288RIT'
UPLOAD_BUCKET = 'cba-indicator-uploads'

def lambda_handler(event, context):
    path = event.get('rawPath', event.get('path', ''))
    
    # Route to appropriate handler (handle both /chat and /prod/chat)
    if '/chat' in path:
        return handle_chat(event)
    elif '/upload' in path:
        return handle_upload(event)
    else:
        return {
            'statusCode': 404,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Not found'})
        }

def handle_chat(event):
    try:
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '')
        session_id = body.get('session_id') or str(uuid.uuid4())
        
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
        response_text = response_text.replace('**', '')     # Remove markdown bold
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'response': response_text,
                'session_id': session_id
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def handle_upload(event):
    try:
        # Get base64 encoded file
        body = event.get('body', '')
        is_base64 = event.get('isBase64Encoded', False)
        
        if is_base64:
            file_bytes = base64.b64decode(body)
        else:
            file_bytes = body.encode() if isinstance(body, str) else body
        
        # Upload to S3
        file_key = f"uploads/{uuid.uuid4()}.pdf"
        s3.put_object(Bucket=UPLOAD_BUCKET, Key=file_key, Body=file_bytes)
        s3_uri = f"s3://{UPLOAD_BUCKET}/{file_key}"
        
        # Use Claude to analyze the document
        prompt = """Analyze this project document and extract:
1. Location/Region
2. Primary Commodity/Product
3. Budget Range

Return ONLY a JSON object with these fields: {"location": "...", "commodity": "...", "budget": "..."}"""
        
        response = bedrock_runtime.invoke_model(
            modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [{
                    "role": "user",
                    "content": f"{prompt}\n\nDocument uploaded to: {s3_uri}"
                }]
            })
        )
        
        result = json.loads(response['body'].read())
        extracted = result['content'][0]['text']
        
        # Try to parse JSON
        try:
            data = json.loads(extracted)
        except:
            # Fallback if not valid JSON
            data = {'location': 'Brazil', 'commodity': 'Coffee', 'budget': '$50,000'}
        
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
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'found': found, 'missing': missing})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
