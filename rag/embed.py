from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

documents = []

for file in os.listdir("documents/processed"):
    
    if file.endswith(".txt"):

        loader = TextLoader(
            os.path.join(
                "documents/processed",
                file
            ),
            encoding = "utf-8"
        )

        docs = loader.load()

        # Add metadata to every document
        for doc in docs:
            doc.metadata["filename"] = file
        
        documents.extend(docs)

print(f"Documents Loaded: {len(documents)}")


splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200
)

chunks = splitter.split_documents(documents)

print("Chunks created:", len(chunks))

embedding_model = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma.from_documents(
    chunks,
    embedding_model,
    persist_directory = "vectorstore"
)

print(f"Vector DB created with {len(chunks)} chunks")