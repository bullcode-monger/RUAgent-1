from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Load the same embedding model used during indexing
embedding_model = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

# Connect to existing vector database
db = Chroma(
    persist_directory = "vectorstore",
    embedding_function = embedding_model
)

# Retrieve relevant documents based on the question
def retrieve_documents(question: str, k: int = 3):
    """"
    Search the vector database and return
    the most relevant chunks
    """

    results = db.similarity_search(
        question,
        k = k
    )

    return results