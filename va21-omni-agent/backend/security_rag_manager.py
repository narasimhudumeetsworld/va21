import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

class SecurityRAGManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        # Ensure the data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

        self.index_path = os.path.join(data_dir, "security_faiss_index")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        if os.path.exists(self.index_path):
            self.vector_store = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
        else:
            # Create a dummy index to start with.
            self.vector_store = FAISS.from_texts(["start"], self.embeddings)
            self.vector_store.save_local(self.index_path)

    def add_texts(self, texts: list[str]):
        """Splits a list of texts into chunks and adds them to the vector store."""
        # The text splitter is good for long documents, but for short texts like titles,
        # it might be better to just wrap them as Documents directly.
        # However, for consistency and to handle potentially longer articles, we'll use the splitter.
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        # Manually create Document objects from the texts
        documents = [Document(page_content=t) for t in texts]

        chunks = text_splitter.split_documents(documents)

        if chunks:
            self.vector_store.add_documents(chunks)
            self.vector_store.save_local(self.index_path)

    def search(self, query, k=5):
        """Performs a similarity search on the vector store."""
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

# Example Usage (for testing purposes)
if __name__ == '__main__':
    # This will create the index in ./data/security_faiss_index
    security_rag = SecurityRAGManager()

    print("Adding texts to the security RAG...")
    test_texts = [
        "A new critical vulnerability, CVE-2025-12345, has been discovered in the popular 'logeverything' library.",
        "Hackers are exploiting a zero-day in Microsoft Exchange servers.",
        "The latest phishing campaign uses QR codes to trick users into giving up their credentials."
    ]
    security_rag.add_texts(test_texts)
    print("Texts added successfully.")

    print("\nSearching for 'vulnerability'...")
    search_results = security_rag.search("vulnerability")
    print("Search Results:")
    for result in search_results:
        print(f"- {result}")

    # Clean up the created index for subsequent runs
    import shutil
    if os.path.exists(security_rag.index_path):
        shutil.rmtree(security_rag.index_path)
        print(f"\nCleaned up index at {security_rag.index_path}")
