import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class ScholarAgent:
    """
    The 'Scholar' is responsible for reading Defense PDFs and answering questions based on them.
    It uses a Vector Database (RAG) to find relevant pages.
    """
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        
        # Switched to Free Local Embeddings (runs on your Mac's CPU/GPU)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize Vector DB
        if os.path.exists(persist_directory):
            self.vector_store = Chroma(
                persist_directory=persist_directory, 
                embedding_function=self.embeddings
            )
        else:
            self.vector_store = None

    def ingest_documents(self, source_directory: str):
        """
        Reads all PDFs from a folder and memorizes them.
        """
        print(f"📚 [SCHOLAR] Reading documents from {source_directory}...")
        
        loader = DirectoryLoader(source_directory, glob="*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        
        # Split text into chunks to fit context window limits
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        
        print(f"Start storing {len(chunks)} memory chunks...")
        
        # Save to ChromaDB
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print("✅ [SCHOLAR] Memorization complete.")

    def query(self, topic: str) -> List[str]:
        """
        Searches the memory for the given topic.
        """
        if not self.vector_store:
            return ["Memory is empty. Please upload documents first."]
            
        results = self.vector_store.similarity_search(topic, k=3)
        return [doc.page_content for doc in results]
