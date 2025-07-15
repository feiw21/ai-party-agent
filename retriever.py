import datasets

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.tools import Tool
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS


# Part 1 Load and prepare dataset
# Load the dataset
guest_dataset = datasets.load_dataset("agents-course/unit3-invitees", split="train")

# Convert dataset entries into Document objects
docs = [
    Document(
        page_content="\n".join([
            f"Name: {guest['name']}",
            f"Relation: {guest['relation']}",
            f"Description: {guest['description']}",
            f"Email: {guest['email']}"
        ]),
        metadata={"name": guest["name"]}
    )
    for guest in guest_dataset
]

# Part 2 Create the retriever tool
# --- Original BM25Retriever code (commented out) ---
# from langchain_community.retrievers import BM25Retriever
# bm25_retriever = BM25Retriever.from_documents(docs)
# def extract_text(query: str) -> str:
#     """Retrieves detailed information about gala guests based on their name or relation."""
#     results = bm25_retriever.invoke(query)
#     if results:
#         return "\n\n".join([doc.page_content for doc in results[:3]])
#     else:
#         return "No matching guest information found."

# --- New FAISS + sentence-transformers code ---
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.from_documents(docs, embedding_model)
vector_retriever = db.as_retriever(search_kwargs={"k": 3})

def extract_text(query: str) -> str:
    """Retrieves detailed information about gala guests based on their name or relation using dense retrieval."""
    results = vector_retriever.invoke(query)
    if results:
        return "\n\n".join([doc.page_content for doc in results])
    else:
        return "No matching guest information found."

guest_info_tool = Tool(
    name="guest_info_retriever",
    func=extract_text,
    description="Retrieves detailed information about gala guests based on their name or relation."
)