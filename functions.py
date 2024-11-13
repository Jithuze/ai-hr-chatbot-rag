import PyPDF2
import chromadb
from chromadb.utils import embedding_functions


def init():

    # Initialize persistent client
    chroma_client = chromadb.PersistentClient(path="assets/vectordb")

    # Embedding function
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
    # Try to get the collection if it exists, otherwise create it

    try:
        # Retrieve the collection if it already exists
        collection = chroma_client.get_collection(name="resume_collection", embedding_function=sentence_transformer_ef)
    except Exception as e:
        # If collection doesn't exist, create a new one
        print(f"Collection doesn't exist. Creating new collection: {e}")
        collection = chroma_client.create_collection(name="resume_collection", embedding_function=sentence_transformer_ef)
    return collection

init()

def add_vector(file, text):

    collection = init()
    # Generate a new ID
    existing_ids = collection.get()["ids"]
    id = str(len(existing_ids) + 1) if existing_ids else '1'

    # Add a single document to the collection
    collection.add(
        documents=[text],
        metadatas=[{"item_id": file}],
        ids=[id]
    )

    print(f"Added entry with ID: {id}")

def search(query):
    collection = init()

    try:
        results = collection.query(
            query_texts=[query],
            n_results=5,  
        )
        if results is None or 'documents' not in results or not results['documents']:
            print("No results found for the query.")
            return None
        print("Found Search Resules...")
        return results
    except Exception as e:
        print(f"Error during search: {e}")
        return None


def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None

def clean_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def ptt(pdf):
    pdf_text = extract_text_from_pdf(pdf)
    text = clean_text(pdf_text)
    return text



# print(search("Python"))