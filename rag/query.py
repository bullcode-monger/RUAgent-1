
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    persist_directory = "vectorstore",
    embedding_function = embedding_model
)

while True:

    question = input("\nAsk a question: ")

    if question.lower() == "exit":
        break

    results = db.similarity_search(
        question,
        k = 3
    )

    for doc in results:
        print("\nMETADATA:\n")
        print(doc.metadata)

    print("\n RESULTS\n")

    sources = []

    for i, doc in enumerate(results):

        print(f"\n----- Result {i + 1} -----\n")
        print(doc.page_content[:1000])

        filename = doc.metadata.get(
            "filename",
            "Unknown"
        )

        sources.append(filename)