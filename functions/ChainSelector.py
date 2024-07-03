from ModifyingPrompt import create_chain
from CreateVector import load_vector_store
from langchain.chains import LLMChain

# Load vector store
vector_store = load_vector_store('docs/static')

# Create retrieval chain
retrieval_chain = create_chain(vector_store)

# Create a simple LLM chain for generic responses
llm_chain = LLMChain(...)  # Initialize this with your desired parameters

def select_chain(input_text):
    if "specific keyword" in input_text.lower():
        return retrieval_chain
    else:
        return llm_chain

def run_chain(input_text):
    chain = select_chain(input_text)
    return chain.run(input_text)
