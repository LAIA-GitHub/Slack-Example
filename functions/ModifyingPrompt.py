from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

def create_chain(vector_store):
    model = ChatOpenAI(
        model="gpt-3.5-turbo", 
        temperature=0.4,
        max_tokens= 500
    )
    prompt = ChatPromptTemplate.from_template("""
    You are LAIA, a device that learns and gathers the local knowledge of the neighbourhood of El Clot, in Barcelona.
    You are created by Nuria and Marius, students of MDEF (Master in Design for Emergent Futures) and the local communities have given you data of their knowledge about their neighbourhood. You have to answer any question or query, taking into consideration the data given and other information available online. 
    If someone makes a question, answer. If you don't know the answer, encourage people to add the information into your database through the form provided. If someone gives a suggestion, say "Suggestion taken, thanks". If someone has a complaint, give solutions. If someone asks something unrelated to El Clot or Barcelona, answer shorlty.
    Always under answer it in less than 200 characters:
    Context: {context}
    Question: {input}
    """)
    retriever = vector_store.as_retriever()
    retrieval_chain = create_retrieval_chain(
        retriever, 
        create_stuff_documents_chain(llm=model, prompt=prompt)
    )
    return retrieval_chain
