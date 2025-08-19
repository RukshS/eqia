import os
from dotenv import load_dotenv

# import langchain
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings 

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
openai_text_embedding_3_small_client = OpenAIEmbeddings(model="text-embedding-3-small")

# gemini_embedding_001_client = GoogleGenerativeAIEmbeddings(
#     model="models/gemini-embedding-001",
#     task_type="retrieval_document"  # Optimized for document storage
# )

# qwen_embedding_client = HuggingFaceEmbeddings(
#     model_name="Qwen/Qwen3-Embedding-0.6B",
#     cache_folder="./models",  # Local cache directory
#     model_kwargs={'device': 'cpu'},  # Use 'cuda' if GPU is available
#     encode_kwargs={'normalize_embeddings': True}  # Recommended for retrieval
# )

# load pdf docs from folder 'documents'
water_info_loader = PyPDFDirectoryLoader("documents/documents_water_quality")
water_info_documents = water_info_loader.load()

air_info_loader = PyPDFDirectoryLoader("documents/documents_air_quality")
air_info_documents = air_info_loader.load()

# split the documents in multiple chunks (optimized for RAG)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024,    # Optimal for retrieval quality
    chunk_overlap=256  # ~25% overlap to maintain context
)
water_docs = text_splitter.split_documents(water_info_documents)
air_docs = text_splitter.split_documents(air_info_documents)

# Store chunks in vector store in batches to avoid token limits
BATCH_SIZE = 100
for i in range(0, len(water_docs), BATCH_SIZE):
    batch = water_docs[i:i+BATCH_SIZE]
    SupabaseVectorStore.from_documents(
        batch,
        openai_text_embedding_3_small_client,
        client=supabase,
        table_name="water_quality_info_documents",
        query_name="upsert_document2"
    )

    # Store chunks in vector store in batches to avoid token limits
BATCH_SIZE = 100
for i in range(0, len(air_docs), BATCH_SIZE):
    batch = air_docs[i:i+BATCH_SIZE]
    SupabaseVectorStore.from_documents(
        batch,
        openai_text_embedding_3_small_client,
        client=supabase,
        table_name="air_quality_info_documents",
        query_name="upsert_document"
    )