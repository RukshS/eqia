#!/usr/bin/env python3
"""
Test script specifically for document retrieval functionality
"""

import asyncio
import aiohttp
import json

async def test_document_retrieval():
    """Test queries that should trigger document retrieval"""
    test_queries = [
        "What is the AQI calculation formula?",
        "How do you measure air quality?", 
        "What are the health effects of poor air quality?",
        "PM2.5 levels and health impacts",
        "Air quality monitoring standards"
    ]
    
    url = "http://127.0.0.1:8000/agent/chat"
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {query}")
        print('='*60)
        
        payload = {"message": query}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"Response status: {result.get('status', 'unknown')}")
                    
                    # Check if tools were used
                    metadata = result.get('metadata', {})
                    tools_used = metadata.get('tools_used', [])
                    
                    if tools_used:
                        print(f"✅ Tools used: {len(tools_used)} tool(s)")
                        for tool in tools_used:
                            print(f"   - {tool.get('tool', 'unknown')}: observation length {tool.get('observation_length', 0)}")
                    else:
                        print("⚠️  No tools used (may indicate vector store issue)")
                    
                    response_text = result.get('response', '')[:200] + "..." if len(result.get('response', '')) > 200 else result.get('response', '')
                    print(f"Response preview: {response_text}")
                    
                else:
                    error_result = await response.json()
                    print(f"❌ Error: {error_result}")
        
        # Small delay between requests
        await asyncio.sleep(1)

async def test_vector_store_directly():
    """Test to see if we can check vector store health"""
    url = "http://127.0.0.1:8000/agent/chat"
    payload = {"message": "test vector store"}
    
    print(f"\n{'='*60}")
    print("Testing Vector Store Health")
    print('='*60)
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            result = await response.json()
            
            metadata = result.get('metadata', {})
            tools_used = metadata.get('tools_used', [])
            
            if tools_used and any('retrieve' in str(tool) for tool in tools_used):
                print("✅ Vector store is working")
            else:
                print("⚠️  Vector store may not be working properly")
                print("Response:", result.get('response', ''))

if __name__ == "__main__":
    print("Testing Document Retrieval Functionality")
    asyncio.run(test_vector_store_directly())
    asyncio.run(test_document_retrieval())
