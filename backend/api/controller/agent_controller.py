import os
import json
import asyncio
import requests
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

class WQIAgentController:
    def __init__(self):
        load_dotenv()
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if supabase_url is None or supabase_key is None:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        self.supabase: Client = create_client(supabase_url, supabase_key)

        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please add it to your .env file.")

        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # Initialize Supabase vector store with explicit function parameters
        try:
            self.vector_store = SupabaseVectorStore(
                embedding=self.embeddings,
                client=self.supabase,
                table_name="water_quality_info_documents",
                query_name="match_aira_water_quality_info_documents",
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

        @tool(description="Retrieve relevant documents about water quality and WQI information based on the query")
        def retrieve_wqi(query: str):
            retrieved_docs = []
            if self.vector_store is not None:
                retrieved_docs = self.vector_store.similarity_search(query, k=16)
            serialized = "\n\n".join(
                f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in retrieved_docs
            ) or "No relevant documents found."
            return serialized

        @tool(description="Search the web using Tavily API for unrelated queries")
        def tavily_search(query: str):
            tavily_api_key = os.environ.get("TAVILY_API_KEY")
            if not tavily_api_key:
                return f"I can't answer this directly. Please use a web search like https://www.tavily.com/ to find your answer for: {query}"
            url = "https://api.tavily.com/search"
            payload = {"query": query, "api_key": tavily_api_key}
            try:
                response = requests.post(url, json=payload, timeout=10)
                if response.ok:
                    data = response.json()
                    return f"Web search result: {data.get('answer', 'No result found.')}"
                else:
                    return f"Tavily search failed: {response.text}"
            except Exception as e:
                return f"Tavily search error: {str(e)}"

        # Only WQI retrieval + Tavily as fallback for out-of-domain queries
        self.tools = [retrieve_wqi, tavily_search]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
               r"You are a helpful assistant specialized exclusively in Water Quality Index (WQI) information. "
              "You must answer only queries related to water quality, water pollution, quality parameters (e.g., pH, turbidity, dissolved oxygen), WQI calculations, standards/guidelines, and related environmental or health impacts. "
              "If the user's question is not about WQI topics, reply: "
              "I can't answer this directly because it is outside the Water Quality Information scope. "
              "Please use a web search like https://www.tavily.com/ to find your answer. "
              "Always provide accurate and helpful responses based on the retrieved information. "
              "Whenever you need to output a mathematical expression, always use LaTeX format, using $...$ for inline math and $$...$$ for block math. "
              "Use $ ... $ instead of (...) for inline LaTeX. Do not use any other delimiters for LaTeX."
             ),
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
        user_input = data.get("message", "")
        async for chunk in self.generate_stream(user_input):
            yield chunk

    async def chat(self, message: str):
        """Handle non-streaming chat requests given a raw message string."""
        try:
            user_input = message or ""
            if not user_input.strip():
                return {"error": "Message cannot be empty", "status": "error"}

            response = await self.agent_executor.ainvoke({"input": user_input})
            agent_output = response.get("output", "")
            intermediate_steps = response.get("intermediate_steps", [])

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
            return {"error": f"Invalid input: {str(e)}", "status": "error"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}", "status": "error"}

    def health_check(self):
        return {"status": "healthy"}
