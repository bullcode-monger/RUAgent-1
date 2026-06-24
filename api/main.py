from fastapi import FastAPI
from pydantic import BaseModel
from api.rag_service import retrieve_documents
from rag.answer import ask_question

#Create the fastAPI appliction
app = FastAPI()

class QuestionRequest(BaseModel):

    question: str    # The question to be asked


@app.post("/ask")    #route decorator to tell FastAPI that this function is the root endpoint   
def ask(data: QuestionRequest):

    answer = ask_question(data.question)
    
    return {
        "question": data.question,
        "answer": answer["answer"],
        "sources": answer["sources"]
    }

