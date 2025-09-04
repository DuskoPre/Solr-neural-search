#!/usr/bin/env python3
"""
Script to generate vector embeddings from text documents.
Based on the Sease tutorial for Apache Solr Neural Search.
"""

from sentence_transformers import SentenceTransformer
import torch
import sys
from itertools import islice
import os

BATCH_SIZE = 100
INFO_UPDATE_FACTOR = 1
MODEL_NAME = 'all-MiniLM-L6-v2'

def load_model():
    """Load or create a SentenceTransformer model."""
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    
    # Get device like 'cuda'/'cpu' that should be used for computation
    if torch.cuda.is_available():
        model = model.to(torch.device("cuda"))
        print(f"Using device: cuda")
    else:
        print(f"Using device: cpu")
    
    return model

def batch_encode_to_vectors(model, input_filename, output_filename):
    """Process documents in batches and generate vector embeddings."""
    print(f"Processing documents from: {input_filename}")
    print(f"Output vectors to: {output_filename}")
    
    # Open the file containing text
    with open(input_filename, 'r', encoding='utf-8') as documents_file:
        # Open the file in which the vectors will be saved
        with open(output_filename, 'w+', encoding='utf-8') as out:
            processed = 0
            # Processing documents in batches
            for n_lines in iter(lambda: tuple(islice(documents_file, BATCH_SIZE)), ()):
                processed += 1
                if processed % INFO_UPDATE_FACTOR == 0:
                    print(f"Processed {processed} batch of documents")
                
                # Create sentence embeddings
                vectors = encode(model, n_lines)
                
                # Write each vector into the output file
                for v in vectors:
                    out.write(','.join([str(i) for i in v]))
                    out.write('\n')

def encode(model, documents):
    """Encode documents into vectors."""
    embeddings = model.encode(documents, show_progress_bar=True)
    print(f'Vector dimension: {len(embeddings[0])}')
    return embeddings

def main():
    if len(sys.argv) != 3:
        print("Usage: python vector_generation.py <input_file> <output_file>")
        print("Example: python vector_generation.py data/documents_10k.tsv data/vectors_documents_10k.tsv")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    
    # Check if input file exists
    if not os.path.exists(input_filename):
        print(f"Error: Input file {input_filename} does not exist!")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Load model
    model = load_model()
    
    # Process documents
    batch_encode_to_vectors(model, input_filename, output_filename)
    
    print("Vector generation completed!")

if __name__ == "__main__":
    main()
