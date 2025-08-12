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
        self.vector_store = SupabaseVectorStore(
            embedding=self.embeddings,
            client=self.supabase,
            table_name="documents",
            query_name="match_eqia_documents",
        )

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

        self.llm = ChatOpenAI(model="gpt-4.1", temperature=0, streaming=True)

        @tool(description="Retrieve relevant documents about air quality and AQI information based on the query", response_format="content_and_artifact")
        def retrieve(query: str):
            retrieved_docs = self.vector_store.similarity_search(query, k=16)
            serialized = "\n\n".join(
                (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
                for doc in retrieved_docs
            )
            return serialized, retrieved_docs

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
            task = asyncio.create_task(
                self.agent_executor.ainvoke({"input": user_input}, config=config)
            )
            last_token_count = 0
            while not callback_handler.finished:
                await asyncio.sleep(0.1)
                current_tokens = callback_handler.tokens[last_token_count:]
                for token in current_tokens:
                    data = json.dumps({"token": token, "type": "token"})
                    yield f"data: {data}\n\n"
                last_token_count = len(callback_handler.tokens)
                if task.done():
                    break
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

    async def chat(self, request):
        data = await request.json()
        user_input = data.get("message", "")
        response = await self.agent_executor.ainvoke({"input": user_input})
        return {"response": response["output"]}

    def health_check(self):
        return {"status": "healthy"}
