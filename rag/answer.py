from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from api.rag_service import retrieve_documents 
import ollama

embedding_model = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    persist_directory = "vectorstore",
    embedding_function = embedding_model
)


def ask_question(question):

    docs = retrieve_documents(question)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # Collect source files
    sources = []

    for doc in docs:

        filename = doc.metadata.get(
            "filename",
            "Unknown"
        )

        if filename not in sources:
            sources.append(filename)

    prompt = f"""

    Use the provided context to answer the question

    Context:
    {context}

    Question:
    {question}
    """

    response = ollama.chat(
        model = "llama3.2",
        messages = [
            {
                "role": "user",
                "content":prompt
            }
        ]
    )

    return {
        "answer": response["message"]["content"],
        "sources": sources
    }


if __name__ == "__main__":

    while True:

        q = input("Ask a question: ")

        result = ask_question(q)

        print("\nANSWER:\n")
        print(result["answer"])

        print("\nSOURCES:\n")

        for source in result["sources"]:
            print(source)

        