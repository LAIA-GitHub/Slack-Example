import os
from dotenv import load_dotenv
from functions  import SupaBaseSetup 
from functions import CreateVector
from functions import ModifyingPrompt
import json
from functions import Chunk

# Load environment variables
load_dotenv()

def rag_processing(input_data, supabase_client): 

    transcription_status = input_data

    # chunk transctription
    # Tokenize and chunk the input message
    #chunks = []
    chunks = Chunk.chunk_input_message(transcription_status)
    print("chunks are:", chunks)

    vector_store_path = 'docs/static'
    # Initialize embeddings
    #embeddings = OpenAIEmbeddings()

    # will give the most relevant chunks of data to the LLM to let it answer your question
    vector_store = CreateVector.load_vector_store(vector_store_path)
    all_retrieved_docs = []

    # run through chunks input message chunks and grabs 4 kwars
    for chunk in chunks:
        retriever = vector_store.as_retriever(search_type="similarity",search_kwargs={"k": 2})
        retrieved_docs = retriever.invoke(chunk)
        all_retrieved_docs.extend(retrieved_docs)

    # Remove duplicates
    all_retrieved_docs = list({doc.page_content: doc for doc in all_retrieved_docs}.values())

    # Check the number of retrieved documents
    print(f"Number of retrieved documents: {len(all_retrieved_docs)}")    
    
    # Prepare the context from retrieved documents
    context_docs = "\n".join([doc.page_content for doc in all_retrieved_docs])
    print("Context to send:", context_docs)

    # Truncate context to ensure it does not exceed token limit
    context_docs = truncate_context(context_docs, 6000)  # Adjust max_tokens as needed


    ##### run RAG 
    #vector_store = CreateVector.load_vector_store('docs/static')
    chain = ModifyingPrompt.create_chain(vector_store)


    # Invoke the chain
    response = chain.invoke({
        "input": input_data,
        "context": context_docs
    })

    llm_answer_status = response['answer'] if isinstance(response, dict) else response   
    print("Answer:", llm_answer_status)
    
    data = {
        "file_uploaded_status": 'in_process',
        "transcription_status": transcription_status,
        "llm_answer_status": llm_answer_status,
    }

    json_response = json.dumps(data)

    SupaBaseSetup.push_data_to_database(supabase_client, transcription_status, llm_answer_status)
    
    return llm_answer_status  # Return the string answer directly



def truncate_context(context, max_tokens):
    tokens = context.split()
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return ' '.join(tokens)