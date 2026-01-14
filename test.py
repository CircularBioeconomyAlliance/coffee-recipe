import json
import uuid

import boto3

client = boto3.client("bedrock-agentcore", region_name="us-west-2")

# Generate a unique session ID (must be 33+ characters)
session_id = f"test-session-{uuid.uuid4()}"
print(f"Using session ID: {session_id}")

payload = json.dumps(
    {
        "prompt": "Give me 5 indicators, their ID's and the methods associated with each, in a table format"
    }
)

response = client.invoke_agent_runtime(
    agentRuntimeArn="arn:aws:bedrock-agentcore:us-west-2:687995992314:runtime/cba_assistant-PkamZO7900",
    runtimeSessionId=session_id,
    payload=payload,
    # qualifier is optional - omitted to use DEFAULT endpoint
)
response_body = response["response"].read()
response_data = json.loads(response_body)
print("Agent Response:", response_data)
