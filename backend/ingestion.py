# import basics
import os
from dotenv import load_dotenv

# import langchain
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings

# import supabase
from supabase.client import Client, create_client

# load environment variables
load_dotenv()  

# initiate supabase db
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
if supabase_url is None or supabase_key is None:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
supabase: Client = create_client(supabase_url, supabase_key)

# initiate embeddings model
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# load pdf docs from folder 'documents'
loader = PyPDFDirectoryLoader("documents")

# split the documents in multiple chunks
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

# store chunks in vector store
# Store chunks in vector store in batches to avoid OpenAI token limit
BATCH_SIZE = 100
for i in range(0, len(docs), BATCH_SIZE):
    batch = docs[i:i+BATCH_SIZE]
    SupabaseVectorStore.from_documents(
        batch,
        embeddings,
        client=supabase,
        table_name="documents",
        query_name="upsert_document",
        chunk_size=1000,
    )