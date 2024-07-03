from functions.ModifyingPrompt import create_chain
from functions.CreateVector import load_vector_store
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import ChatPromptTemplate

# Load vector store
vector_store = load_vector_store('docs/static')

# Create retrieval chain
retrieval_chain = create_chain(vector_store)

# Create a simple LLM chain for generic responses
llm = OpenAI(temperature=0.4)
prompt_template = ChatPromptTemplate.from_template("You are a helpful assistant. Answer the following question: {input}")
llm_chain = LLMChain(prompt=prompt_template, llm=llm)

def select_chain(input_text):
    if "specific keyword" in input_text.lower():
        return retrieval_chain
    else:
        return llm_chain

def run_chain(input_text):
    chain = select_chain(input_text)
    return chain.run(input_text)
