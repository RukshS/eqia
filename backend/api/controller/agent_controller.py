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
                    k=5,
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

        self.tools = [retrieve]
        # Update the system prompt to instruct the model to use latex_tool for all math output
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", r"You are a helpful assistant specialized in Air Quality Index (AQI) information."
            "You are to find relevant information about air quality, pollution, AQI calculations, health impacts, and related topics."
            "Always provide accurate and helpful responses based on the retrieved information."
            "Whenever you need to output a mathematical expression, always use LaTex format it, using $...$ for inline math and $$...$$ for block math."
            "Use $ ... $ instead of (...) for inline Latex. Do not use any other delimiters for LaTeX."
            "Avoid answering anything other than air quality and air pollution and air related"),
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
