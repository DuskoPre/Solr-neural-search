#!/usr/bin/env python3
"""
Script to convert text queries into vector embeddings for KNN search.
Based on the Sease tutorial for Apache Solr Neural Search.
"""

from sentence_transformers import SentenceTransformer
import sys
import json

MODEL_NAME = 'all-MiniLM-L6-v2'

def load_model():
    """Load the sentence transformer model."""
    print(f"Loading model: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)

def vectorize_query(model, query):
    """Convert a text query into a vector embedding."""
    print(f"Vectorizing query: '{query}'")
    
    # Encode the query
    embeddings = model.encode([query])
    vector = embeddings[0].tolist()
    
    print(f"Generated vector with {len(vector)} dimensions")
    return vector

def main():
    if len(sys.argv) < 2:
        print("Usage: python query_vectorizer.py <query_text> [--json]")
        print("Examples:")
        print("  python query_vectorizer.py 'what is a bank transit number'")
        print("  python query_vectorizer.py 'what is a bank transit number' --json")
        sys.exit(1)
    
    query = sys.argv[1]
    output_json = len(sys.argv) > 2 and sys.argv[2] == '--json'
    
    # Load model
    model = load_model()
    
    # Vectorize query
    vector = vectorize_query(model, query)
    
    if output_json:
        # Output as JSON for easier parsing
        result = {
            "query": query,
            "vector": vector,
            "dimension": len(vector)
        }
        print(json.dumps(result, indent=2))
    else:
        # Output as comma-separated values
        print("Vector:")
        print(','.join([str(v) for v in vector]))

if __name__ == "__main__":
    main()
