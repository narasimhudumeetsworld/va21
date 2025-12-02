import os
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

class RAGManager:
    def __init__(self, data_dir="data", db_path=None):
        self.data_dir = data_dir
        self.index_path = os.path.join(data_dir, db_path or "faiss_index")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # Ensure the data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

        if os.path.exists(self.index_path):
            self.vector_store = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
        else:
            # Create a dummy index to start with
            # This is necessary because FAISS.from_documents requires a list of documents
            # and we might not have any when the app starts for the first time.
            # We will add real documents later.
            self.vector_store = FAISS.from_texts(["start"], self.embeddings)
            self.vector_store.save_local(self.index_path)


    def add_document(self, file_path):
        """Loads a document, splits it into chunks, and adds it to the vector store."""
        file_extension = os.path.splitext(file_path)[1]
        if file_extension == ".pdf":
            loader = PyPDFLoader(file_path)
        elif file_extension == ".txt" or file_extension == ".md":
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        self.vector_store.add_documents(chunks)
        self.vector_store.save_local(self.index_path)

    def create_new_index(self, texts: list):
        """Create a new FAISS index from a list of texts, replacing the existing one."""
        if not texts:
            return
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_chunks = []
        
        for text in texts:
            chunks = text_splitter.split_text(text)
            all_chunks.extend(chunks)
        
        if all_chunks:
            self.vector_store = FAISS.from_texts(all_chunks, self.embeddings)
            self.vector_store.save_local(self.index_path)

    def search(self, query, k=5):
        """Performs a similarity search on the vector store."""
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]
