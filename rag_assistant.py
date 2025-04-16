import os
import sys
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import Ollama

def setup_vector_db():
    """Load JSONL data, create embeddings and store in ChromaDB"""
    # Check if vector DB already exists
    if os.path.exists("college_faq_index") and os.path.isdir("college_faq_index"):
        print("Vector database already exists. Loading existing database...")
        return True
        
    # Check if data file exists - prioritize college_admissions_dataset.jsonl in root directory
    data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "college_admissions_dataset.jsonl")
    if not os.path.exists(data_file):
        # Try to use college_faq.jsonl as fallback
        fallback_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "college_faq.jsonl")
        if os.path.exists(fallback_file):
            data_file = fallback_file
            print(f"Using fallback dataset: {data_file}")
        else:
            print(f"Error: Missing dataset file {data_file}")
            return False
    
    try:
        print(f"Loading data from {data_file}...")
        # Load JSONL data
        loader = JSONLoader(
            file_path=data_file, 
            jq_schema='.', 
            content_key='response',
            metadata_func=lambda x: {"question": x.get("prompt", "")},
            text_content=False
        )
        docs = loader.load()
        print(f"Loaded {len(docs)} documents")
        
        # Split docs
        print("Splitting documents into chunks...")
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        print(f"Created {len(chunks)} chunks")
        
        # Add debug output to verify document content
        if chunks:
            print(f"Sample chunk content: {chunks[0].page_content[:100]}...")
            print(f"Sample chunk metadata: {chunks[0].metadata}")
        
        # Embed and store
        print("Creating embeddings and storing in vector database...")
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        db = Chroma.from_documents(chunks, embedding, persist_directory="college_faq_index")
        db.persist()
        print("Vector database created and persisted successfully")
        return True
        
    except Exception as e:
        print(f"Error setting up vector database: {str(e)}")
        return False

def preprocess_query(query_text):
    """Preprocess the query to handle typos and partial keyword matches"""
    # List of common college-related keywords
    college_keywords = [
        "college", "university", "campus", "school", "admission", "apply", "application",
        "fee", "tuition", "scholarship", "financial", "enroll", "course", "program",
        "major", "degree", "dorm", "housing", "student", "faculty", "professor", "class",
        "semester", "quarter", "academic", "study", "deadline", "requirement",
        "test", "exam", "sat", "act", "gpa", "grade", "transcript", "essay"
    ]
    
    # Check for fuzzy matches with college keywords
    words = query_text.lower().split()
    for i, word in enumerate(words):
        # Skip very short words (less than 3 chars)
        if len(word) < 3:
            continue
            
        for keyword in college_keywords:
            # Skip keywords that are too different in length
            if abs(len(word) - len(keyword)) > 3:
                continue
                
            # Check for partial match (word contains keyword or keyword contains word)
            if word in keyword or keyword in word:
                print(f"Partial keyword match: '{word}' matches '{keyword}'")
                words[i] = keyword  # Replace with correct keyword
                break
                
            # Simple character-based similarity (at least 70% of chars match)
            common_chars = sum(c in keyword for c in word)
            if common_chars >= 0.7 * len(word):
                print(f"Fuzzy keyword match: '{word}' corrected to '{keyword}'")
                words[i] = keyword  # Replace with correct keyword
                break
    
    # Reconstruct the query with corrected words
    processed_query = " ".join(words)
    if processed_query != query_text.lower():
        print(f"Original query: '{query_text}'")
        print(f"Processed query: '{processed_query}'")
    
    return processed_query

def query_rag_model(query_text):
    """Query the RAG model with the given text"""
    try:
        # Preprocess query to handle typos and partial matches
        processed_query = preprocess_query(query_text)
        
        # Load embedding model
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Load DB
        db = Chroma(persist_directory="college_faq_index", embedding_function=embedding)
        
        # Init LLM (Gemma 2B running via Ollama)
        llm = Ollama(model="gemma:2b")
        
        # Create QA chain with improved retrieval parameters
        retriever = db.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 5,  # Retrieve more documents for better context
                "score_threshold": 0.5  # Only include relevant matches
            }
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": f"Based on the following context, answer the question. If the answer is not in the context, say 'I don't have information about that in my knowledge base.'\n\nContext: {{context}}\n\nQuestion: {{question}}\n\nAnswer:"
            }
        )
        
        # Run query with the processed query text
        result = qa_chain({"query": processed_query})
        
        # Return formatted result
        answer = result["result"]
        sources = [doc.page_content for doc in result["source_documents"]]
        
        return {
            "answer": answer,
            "sources": sources
        }
        
    except Exception as e:
        print(f"Error querying RAG model: {str(e)}")
        return {"error": str(e)}

def interactive_mode():
    """Run an interactive session with the RAG model"""
    print("=== College Admissions RAG Assistant ===\n")
    print("Type 'exit' to quit\n")
    
    while True:
        query = input("\nYour question: ")
        if query.lower() in ["exit", "quit", "q"]:
            break
            
        print("\nSearching knowledge base...")
        result = query_rag_model(query)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            continue
            
        print("\n=== Answer ===\n")
        print(result["answer"])
        
        # Optionally show sources
        if result["sources"] and len(result["sources"]) > 0:
            print("\n=== Sources ===\n")
            for i, source in enumerate(result["sources"], 1):
                print(f"Source {i}: {source[:150]}..." if len(source) > 150 else source)

def main():
    # Check dependencies
    try:
        import langchain
        import chromadb
    except ImportError:
        print("Error: Required packages not installed.")
        print("Please install with: pip install langchain chromadb sentence-transformers")
        return
    
    # Setup vector database
    if not setup_vector_db():
        print("Failed to set up vector database. Exiting.")
        return
    
    # Check if Ollama is running and has the required model
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        if not response.ok:
            print("Error: Ollama server not running. Please start Ollama first.")
            return
            
        # Check if gemma:2b model is available
        models = response.json().get("models", [])
        model_names = [model.get("name") for model in models]
        if "gemma:2b" not in model_names:
            print("Warning: gemma:2b model not found in Ollama.")
            print("Please run: ollama pull gemma:2b")
            return
    except Exception as e:
        print(f"Error checking Ollama: {str(e)}")
        print("Please ensure Ollama is running with: ollama serve")
        return
    
    # Start interactive mode
    interactive_mode()

if __name__ == "__main__":
    main()