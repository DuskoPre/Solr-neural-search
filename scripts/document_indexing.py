#!/usr/bin/env python3
"""
Script to index documents with vector embeddings into Solr.
Based on the Sease tutorial for Apache Solr Neural Search.
"""

import sys
import pysolr
import os

# Solr configuration
SOLR_ADDRESS = os.getenv('SOLR_URL', 'http://localhost:8983/solr/ms-marco')
BATCH_SIZE = 100

def create_solr_client():
    """Create a Solr client instance."""
    print(f"Connecting to Solr at: {SOLR_ADDRESS}")
    return pysolr.Solr(SOLR_ADDRESS, always_commit=True, timeout=10)

def index_documents(solr, documents_filename, embedding_filename):
    """Index documents with their corresponding vectors into Solr."""
    print(f"Indexing documents from: {documents_filename}")
    print(f"Using vectors from: {embedding_filename}")
    
    # Open the file containing text
    with open(documents_filename, "r", encoding="utf-8") as documents_file:
        # Open the file containing vectors
        with open(embedding_filename, "r", encoding="utf-8") as vectors_file:
            documents = []
            
            # For each document, create a JSON document including both text and related vector
            for index, (document, vector_string) in enumerate(zip(documents_file, vectors_file)):
                try:
                    # Parse vector string to float array
                    vector = [float(w) for w in vector_string.strip().split(",")]
                    
                    # Create document
                    doc = {
                        "id": str(index),
                        "text": document.strip(),
                        "vector": vector
                    }
                    
                    # Append JSON document to list
                    documents.append(doc)
                    
                    # Index batches of documents at a time
                    if index % BATCH_SIZE == 0 and index != 0:
                        # Index data to Solr
                        solr.add(documents)
                        documents = []
                        print(f"==== Indexed {index} documents ======")
                
                except ValueError as e:
                    print(f"Error processing document {index}: {e}")
                    continue
            
            # Index the remaining documents when list < BATCH_SIZE
            if documents:
                solr.add(documents)
                print(f"==== Indexed remaining {len(documents)} documents ======")
    
    print("Indexing finished!")

def test_connection(solr):
    """Test the connection to Solr."""
    try:
        # Perform a simple ping
        result = solr.ping()
        print(f"Solr connection test successful: {result}")
        return True
    except Exception as e:
        print(f"Error connecting to Solr: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python document_indexing.py <documents_file> <vectors_file>")
        print("Example: python document_indexing.py data/documents_10k.tsv data/vectors_documents_10k.tsv")
        sys.exit(1)
    
    documents_filename = sys.argv[1]
    embedding_filename = sys.argv[2]
    
    # Check if input files exist
    if not os.path.exists(documents_filename):
        print(f"Error: Documents file {documents_filename} does not exist!")
        sys.exit(1)
    
    if not os.path.exists(embedding_filename):
        print(f"Error: Vectors file {embedding_filename} does not exist!")
        sys.exit(1)
    
    # Create Solr client
    solr = create_solr_client()
    
    # Test connection
    if not test_connection(solr):
        print("Failed to connect to Solr. Please ensure Solr is running.")
        sys.exit(1)
    
    # Index documents
    try:
        index_documents(solr, documents_filename, embedding_filename)
    except Exception as e:
        print(f"Error during indexing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
