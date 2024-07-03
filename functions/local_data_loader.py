from langchain.document_loaders import DirectoryLoader

def load_local_documents(directory_path, glob_pattern="**/*.csv", multithreaded=True):
    loader = DirectoryLoader(directory_path, glob=glob_pattern, use_multithreading=multithreaded)
    return loader.load()
