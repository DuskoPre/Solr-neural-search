#!/usr/bin/env python3
"""
Sample data generator for testing neural search functionality.
Creates sample documents similar to MS MARCO dataset.
"""

import os
import sys

def create_sample_documents():
    """Create sample documents for testing."""
    
    sample_docs = [
        "A federal tax identification number (also known as an employer identification number or EIN), is a number assigned solely to your business by the IRS.",
        "A federal tax identification number is used to identify your business to several federal agencies responsible for the regulation of business.",
        "Let's start at the beginning. A tax ID number or employer identification number (EIN) is a number assigned to a business, much like a social security number does for a person.",
        "The bank routing number is a 9-digit number that identifies the financial institution where your account is held.",
        "A routing number, also known as an ABA number or routing transit number, is used to identify a specific bank or credit union.",
        "Bank transit numbers are used for electronic transfers, direct deposits, and automatic bill payments.",
        "Financial institutions use routing numbers to process checks, wire transfers, and ACH transactions.",
        "The Federal Reserve uses routing numbers to process Fedwire funds transfers and automated clearing house transactions.",
        "Credit unions and banks are assigned unique routing numbers by the American Bankers Association.",
        "Electronic fund transfers require both the bank routing number and the account number to complete the transaction.",
        "The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was. The only cloud hanging over the impressive achievement of the atomic researchers and engineers is what their success truly meant; hundreds of thousands of innocent lives obliterated.",
        "The 23,000-square-mile (60,000 km2) Matanuska-Susitna Borough was established in 1964 with the merger of the Matanuska-Susitna Borough and part of the former Valdez-Cordova Census Area. The borough seat is Palmer, and the largest city is Wasilla.",
        "The researchers were in Baltimore on Tuesday to present their findings at a medical conference. The study's results were more promising than initially believed.",
        "Neural networks are computing systems inspired by biological neural networks that constitute animal brains. Such systems learn to perform tasks by considering examples, generally without being programmed with task-specific rules.",
        "Machine learning is a method of data analysis that automates analytical model building. It is a branch of artificial intelligence based on the idea that systems can learn from data, identify patterns and make decisions with minimal human intervention.",
        "Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning.",
        "Natural language processing combines computational linguistics with statistical, machine learning, and deep learning models to give computers the ability to process human language.",
        "Vector embeddings are numerical representations of data that capture semantic meaning and relationships between different items in a high-dimensional space.",
        "Semantic search uses meaning and context rather than just keyword matching to provide more relevant search results.",
        "Information retrieval systems help users find information that matches their information needs from large collections of documents or data."
    ]
    
    return sample_docs

def save_documents(docs, filename):
    """Save documents to a file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        for doc in docs:
            f.write(doc + '\n')
    
    print(f"Saved {len(docs)} documents to {filename}")

def main():
    """Generate sample data files."""
    
    # Create data directory if it doesn't exist
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate sample documents
    docs = create_sample_documents()
    
    # Save to file
    documents_file = os.path.join(data_dir, "sample_documents.tsv")
    save_documents(docs, documents_file)
    
    print(f"\nSample data generated successfully!")
    print(f"Documents file: {documents_file}")
    print(f"Total documents: {len(docs)}")
    print(f"\nNext steps:")
    print(f"1. Generate vectors: python scripts/vector_generation.py {documents_file} data/sample_vectors.tsv")
    print(f"2. Index documents: python scripts/document_indexing.py {documents_file} data/sample_vectors.tsv")
    print(f"3. Run tests: python scripts/neural_search_tester.py all")

if __name__ == "__main__":
    main()
