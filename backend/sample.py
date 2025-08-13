import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# Initialize the LangChain Google embeddings
embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

texts = [
    "What is the meaning of life?",
    "What is the purpose of existence?",
    "How do I bake a cake?"
]

# Use LangChain's embed_documents method
result = embeddings_model.embed_documents(texts)
print(len(result[0]))

# Calculate cosine similarity. Higher scores = greater semantic similarity.

embeddings_matrix = np.array(result)
similarity_matrix = cosine_similarity(embeddings_matrix)

for i, text1 in enumerate(texts):
    for j in range(i + 1, len(texts)):
        text2 = texts[j]
        similarity = similarity_matrix[i, j]
        print(f"Similarity between '{text1}' and '{text2}': {similarity:.4f}")