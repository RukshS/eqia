import os
import json
import asyncio
from dotenv import load_dotenv
from typing import AsyncGenerator
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from supabase.client import Client, create_client
from langchain_core.tools import tool
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.runnables import RunnableConfig

class AQIAgentController:
    def __init__(self):
        load_dotenv()
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if supabase_url is None or supabase_key is None:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        self.supabase: Client = create_client(supabase_url, supabase_key)

        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please add it to your .env file.")

        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        
        # Initialize Supabase vector store with explicit function parameters
        try:
            self.vector_store = SupabaseVectorStore(
                embedding=self.embeddings,
                client=self.supabase,
                table_name="documents",
                query_name="match_eqia_documents",
                # Add these parameters to help with function overloading
                chunk_size=1000
            )
        except Exception as e:
            print(f"Warning: Vector store initialization failed: {e}")
            print("The system will work without document retrieval.")
            self.vector_store = None

        class StreamingCallbackHandler(AsyncCallbackHandler):
            def __init__(self):
                self.tokens = []
                self.finished = False

            async def on_llm_new_token(self, token: str, **kwargs) -> None:
                self.tokens.append(token)

            async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
                self.finished = True

            async def on_agent_action(self, action, **kwargs) -> None:
                self.tokens.append(f"\n🔍 Using tool: {action.tool}\n")

            async def on_agent_finish(self, finish, **kwargs) -> None:
                self.finished = True

        self.StreamingCallbackHandler = StreamingCallbackHandler

        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)

        @tool(description="Retrieve relevant documents about air quality and AQI information based on the query", response_format="content_and_artifact")
        def retrieve(query: str):
            if self.vector_store is None:
                return "Vector store is not available. Please check your Supabase configuration.", []
            
            try:
                # Use similarity_search with fewer results and timeout handling
                retrieved_docs = self.vector_store.similarity_search(
                    query, 
                    k=8,
                    filter=None  # Use None instead of empty dict
                )
                
                if not retrieved_docs:
                    return "No relevant documents found for this query.", []
                
                serialized = "\n\n".join(
                    (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
                    for doc in retrieved_docs
                )
                return serialized, retrieved_docs
            except Exception as e:
                error_msg = str(e)
                if "statement timeout" in error_msg.lower():
                    return "Search timed out. Try a more specific query.", []
                elif "could not choose" in error_msg.lower():
                    # Try alternative approach for function overloading issue
                    try:
                        retrieved_docs = self.vector_store.similarity_search(query, k=3)
                        serialized = "\n\n".join(
                            (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
                            for doc in retrieved_docs
                        )
                        return serialized, retrieved_docs
                    except Exception as e2:
                        return f"Error retrieving documents: {str(e2)}", []
                else:
                    return f"Error retrieving documents: {error_msg}", []

        @tool(description="Search the internet for current information about environmental quality, air pollution, water quality, soil monitoring, or related topics when local documents don't have sufficient information")
        def web_search(query: str) -> str:
            """
            Search the internet for environmental and air quality information.
            Use this tool when the retrieved documents don't contain sufficient information
            or when current/recent data is needed.
            """
            try:
                import requests
                
                # DuckDuckGo instant answer API
                ddg_url = "https://api.duckduckgo.com/"
                
                # First try a simple query
                simple_params = {
                    'q': query,
                    'format': 'json'
                }
                
                response = requests.get(ddg_url, params=simple_params, timeout=10)
                
                # Accept both 200 and 202 status codes
                if response.status_code in [200, 202]:
                    data = response.json()
                    
                    # Extract relevant information
                    results = []
                    
                    # Add abstract if available
                    if data.get('Abstract') and data['Abstract'].strip():
                        results.append(f"Summary: {data['Abstract']}")
                    
                    # Add definition if available
                    if data.get('Definition') and data['Definition'].strip():
                        results.append(f"Definition: {data['Definition']}")
                    
                    # Add related topics
                    if data.get('RelatedTopics'):
                        related_count = 0
                        for topic in data['RelatedTopics']:
                            if isinstance(topic, dict) and topic.get('Text') and related_count < 3:
                                # Clean up the text (remove HTML tags if any)
                                topic_text = topic['Text'].replace('<a href="', '').replace('</a>', '')
                                if len(topic_text) > 50:  # Only include substantial content
                                    results.append(f"Related: {topic_text}")
                                    related_count += 1
                    
                    if results:
                        return f"Web search results for '{query}':\n\n" + "\n\n".join(results)
                    else:
                        # If no specific results, try to extract any useful info from the response
                        if data.get('AbstractText') and data['AbstractText'].strip():
                            return f"Web search found: {data['AbstractText']}"
                        else:
                            # Fallback: provide general guidance
                            return f"""No specific web results found for '{query}', but here's general guidance:

For environmental quality monitoring, key areas to consider include:

**Air Quality Parameters:**
- PM2.5 and PM10 particulate matter
- Ozone (O3) levels
- Nitrogen dioxide (NO2)
- Sulfur dioxide (SO2)
- Carbon monoxide (CO)

**Water Quality Indicators:**
- pH levels, dissolved oxygen, turbidity
- Chemical and biological contaminants

**Soil Quality Factors:**
- Nutrient content, pH balance
- Heavy metal contamination
- Organic matter content

For current, location-specific data, consult local environmental agencies or monitoring stations."""
                else:
                    return f"Web search failed with status code: {response.status_code}. Please try a more specific query."
                    
            except Exception as e:
                if "timeout" in str(e).lower():
                    return "Web search timed out. Please try a more specific query."
                else:
                    return f"Web search error: {str(e)}. Using fallback environmental guidance instead."

        self.tools = [retrieve, web_search]
        # Update the system prompt to instruct the model to use both tools appropriately
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", r"You are a helpful assistant specialized in Environmental Quality (Air, Water, Soil) information and monitoring."
            "You have access to two main tools:"
            "\n1. 'retrieve' - to search local documents for air quality, environmental monitoring information"
            "\n2. 'web_search' - to search the internet for current information when local documents are insufficient"
            "\n\nAlways try to retrieve information from local documents first. If the retrieved information is insufficient, incomplete, or you need current data, use the web_search tool."
            "\n\nWhen providing answers:"
            "- Always provide accurate and helpful responses based on the retrieved or searched information"
            "- Cite your sources when possible"
            "- For mathematical expressions, always use LaTeX format: $...$ for inline math and $$...$$ for block math"
            "- Use $ ... $ instead of (...) for inline LaTeX. Do not use any other delimiters for LaTeX"
            "- Focus on environmental quality, air pollution, water quality, soil monitoring, and related topics"
            "- If asked about unrelated topics, politely redirect to environmental monitoring topics"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    async def generate_stream(self, user_input: str) -> AsyncGenerator[str, None]:
        try:
            callback_handler = self.StreamingCallbackHandler()
            config: RunnableConfig = {"callbacks": [callback_handler]}
            
            # Start the agent execution task
            task = asyncio.create_task(
                self.agent_executor.ainvoke({"input": user_input}, config=config)
            )
            
            last_token_count = 0
            
            # Stream tokens as they come in
            while not task.done() or last_token_count < len(callback_handler.tokens):
                await asyncio.sleep(0.05)  # Reduced sleep time for better responsiveness
                
                # Send new tokens
                current_tokens = callback_handler.tokens[last_token_count:]
                for token in current_tokens:
                    data = json.dumps({"token": token, "type": "token"})
                    yield f"data: {data}\n\n"
                
                last_token_count = len(callback_handler.tokens)
            
            # Get the final result
            try:
                result = await task
                final_data = json.dumps({
                    "token": "",
                    "type": "end",
                    "full_response": result.get("output", "")
                })
                yield f"data: {final_data}\n\n"
            except Exception as e:
                error_data = json.dumps({
                    "token": f"\nError: {str(e)}",
                    "type": "error"
                })
                yield f"data: {error_data}\n\n"
                
        except Exception as e:
            error_data = json.dumps({
                "token": f"\nStream Error: {str(e)}",
                "type": "error"
            })
            yield f"data: {error_data}\n\n"

    async def generate_stream_from_request(self, request):
        data = await request.json()
        user_input = data.get("message", "")  # Changed from "me" to "message" for consistency
        async for chunk in self.generate_stream(user_input):
            yield chunk

    async def chat(self, request):
        """
        Handle non-streaming chat requests with proper error handling and response formatting
        """
        try:
            data = await request.json()
            user_input = data.get("message", "")
            
            if not user_input.strip():
                return {
                    "error": "Message cannot be empty",
                    "status": "error"
                }
            
            # Execute the agent
            response = await self.agent_executor.ainvoke({"input": user_input})
            
            # Extract and format the response
            agent_output = response.get("output", "")
            intermediate_steps = response.get("intermediate_steps", [])
            
            # Format tool usage information
            tools_used = []
            for step in intermediate_steps:
                if hasattr(step, '__len__') and len(step) >= 2:
                    action, observation = step[0], step[1]
                    tools_used.append({
                        "tool": getattr(action, 'tool', 'unknown'),
                        "tool_input": getattr(action, 'tool_input', {}),
                        "observation_length": len(str(observation)) if observation else 0
                    })
            
            return {
                "response": agent_output,
                "status": "success",
                "metadata": {
                    "tools_used": tools_used,
                    "input_length": len(user_input),
                    "output_length": len(agent_output)
                }
            }
            
        except ValueError as e:
            return {
                "error": f"Invalid input: {str(e)}",
                "status": "error"
            }
        except Exception as e:
            return {
                "error": f"An error occurred: {str(e)}",
                "status": "error"
            }

    def health_check(self):
        return {"status": "healthy"}
