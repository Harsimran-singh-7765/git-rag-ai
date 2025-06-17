 # qa_bot.py
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

def ask_question(query: str, vectorstore):
    # Load Gemini chat model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.4
    )

    # Setup RAG pipeline (retriever + Gemini)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        return_source_documents=False
    )

    result = qa.run(query)
    return result

