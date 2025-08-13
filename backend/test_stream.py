#!/usr/bin/env python3
"""
Test script for the chat streaming endpoint
"""

import asyncio
import aiohttp
import json

async def test_stream():
    """Test the streaming chat endpoint"""
    url = "http://127.0.0.1:8000/agent/chat/stream"
    payload = {"message": "What is AQI and how is it calculated?"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            print(f"Status: {response.status}")
            print(f"Headers: {response.headers}")
            print("\nStreaming response:")
            print("-" * 50)
            
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    try:
                        parsed = json.loads(data)
                        if parsed.get('type') == 'token':
                            print(parsed['token'], end='', flush=True)
                        elif parsed.get('type') == 'end':
                            print(f"\n\nFull response: {parsed.get('full_response', 'N/A')}")
                        elif parsed.get('type') == 'error':
                            print(f"\nError: {parsed['token']}")
                    except json.JSONDecodeError:
                        print(f"Invalid JSON: {data}")

async def test_regular_chat():
    """Test the regular chat endpoint"""
    url = "http://127.0.0.1:8000/agent/chat"
    payload = {"message": "What is PM2.5?"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            print(f"\nRegular chat status: {response.status}")
            result = await response.json()
            print(f"Response status: {result.get('status', 'unknown')}")
            print(f"Response: {result.get('response', 'No response')}")
            
            if result.get('metadata'):
                metadata = result['metadata']
                print(f"Tools used: {metadata.get('tools_used', [])}")
                print(f"Input length: {metadata.get('input_length', 0)}")
                print(f"Output length: {metadata.get('output_length', 0)}")
            
            if result.get('status') == 'error':
                print(f"Error: {result.get('error', 'Unknown error')}")

async def test_tools_endpoint():
    """Test the tools info endpoint"""
    url = "http://127.0.0.1:8000/agent/tools"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"\nTools endpoint status: {response.status}")
            result = await response.json()
            print(f"Total tools: {result.get('total_tools', 0)}")
            
            for tool in result.get('tools', []):
                print(f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")

async def test_health_endpoint():
    """Test the health check endpoint"""
    url = "http://127.0.0.1:8000/agent/health"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"\nHealth check status: {response.status}")
            result = await response.json()
            print(f"Health status: {result.get('status', 'unknown')}")

if __name__ == "__main__":
    print("Testing streaming endpoint...")
    asyncio.run(test_stream())
    
    print("\n" + "="*60)
    print("Testing regular chat endpoint...")
    asyncio.run(test_regular_chat())
    
    print("\n" + "="*60)
    print("Testing tools endpoint...")
    asyncio.run(test_tools_endpoint())
    
    print("\n" + "="*60)
    print("Testing health endpoint...")
    asyncio.run(test_health_endpoint())
