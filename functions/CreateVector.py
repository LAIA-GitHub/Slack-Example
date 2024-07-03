from venv import create
from dotenv import load_dotenv
load_dotenv()


from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS


def create_vector_store(docs):
    embedding = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(docs, embedding=embedding)
    vector_store.save_local('../docs/static')
    return vector_store

def load_vector_store(store_path: str) -> FAISS:
    vector_store = FAISS.load_local(store_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    return vector_store


