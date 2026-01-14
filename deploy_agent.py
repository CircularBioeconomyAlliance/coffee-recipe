#!/usr/bin/env python3
"""Deploy the CBA agent to Amazon Bedrock AgentCore Runtime."""

import boto3
import sys

def deploy_agent(agent_name, container_uri, role_arn, region="us-west-2"):
    """
    Deploy agent to Bedrock AgentCore Runtime.
    
    Args:
        agent_name: Name for the agent runtime
        container_uri: ECR container image URI
        role_arn: IAM role ARN for the agent
        region: AWS region (default: us-west-2)
    """
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        
        print(f"Creating agent runtime: {agent_name}")
        print(f"Container URI: {container_uri}")
        print(f"Role ARN: {role_arn}")
        print(f"Region: {region}")
        
        response = client.create_agent_runtime(
            agentRuntimeName=agent_name,
            agentRuntimeArtifact={
                'containerConfiguration': {
                    'containerUri': container_uri
                }
            },
            networkConfiguration={"networkMode": "PUBLIC"},
            roleArn=role_arn
        )
        
        print("\n✅ Agent Runtime created successfully!")
        print(f"Agent Runtime ARN: {response['agentRuntimeArn']}")
        print(f"Status: {response['status']}")
        
        return response
        
    except Exception as e:
        print(f"\n❌ Error deploying agent: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Configuration - Update these values for your deployment
    AGENT_NAME = "cba-indicator-agent"
    CONTAINER_URI = "<account-id>.dkr.ecr.us-west-2.amazonaws.com/cba-agent:latest"
    ROLE_ARN = "arn:aws:iam::<account-id>:role/AgentRuntimeRole"
    REGION = "us-west-2"
    
    print("=" * 60)
    print("CBA Agent Deployment to Bedrock AgentCore Runtime")
    print("=" * 60)
    print("\n⚠️  Before running this script, ensure you have:")
    print("1. Built and pushed your container to ECR")
    print("2. Created an IAM role with appropriate permissions")
    print("3. Updated CONTAINER_URI and ROLE_ARN in this script")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    deploy_agent(AGENT_NAME, CONTAINER_URI, ROLE_ARN, REGION)
