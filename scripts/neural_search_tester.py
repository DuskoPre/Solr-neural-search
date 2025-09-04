#!/usr/bin/env python3
"""
Comprehensive testing script for Apache Solr Neural Search functionality.
Implements all methods from the Sease tutorial.
"""

import requests
import json
import sys
import os
from sentence_transformers import SentenceTransformer

SOLR_URL = os.getenv('SOLR_URL', 'http://localhost:8983/solr/ms-marco')
MODEL_NAME = 'all-MiniLM-L6-v2'

class NeuralSearchTester:
    def __init__(self):
        self.solr_url = SOLR_URL
        self.model = SentenceTransformer(MODEL_NAME)
        print(f"Initialized Neural Search Tester")
        print(f"Solr URL: {self.solr_url}")
    
    def vectorize_query(self, query):
        """Convert text query to vector."""
        embeddings = self.model.encode([query])
        return embeddings[0].tolist()
    
    def make_request(self, endpoint, data=None, method='GET'):
        """Make HTTP request to Solr."""
        url = f"{self.solr_url}{endpoint}"
        
        try:
            if method == 'POST':
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                response = requests.get(url, timeout=30)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None
    
    def test_basic_knn_query(self, query="what is a bank transit number", top_k=3):
        """Test 1: Basic KNN Query"""
        print(f"\n=== Test 1: Basic KNN Query ===")
        print(f"Query: '{query}'")
        print(f"TopK: {top_k}")
        
        # Vectorize query
        vector = self.vectorize_query(query)
        
        # Build KNN query
        query_data = {
            "query": f"{{!knn f=vector topK={top_k}}}{vector}"
        }
        
        # Execute query
        result = self.make_request("/select?fl=id,text,score", query_data, 'POST')
        
        if result:
            print(f"Found {result['response']['numFound']} documents")
            for i, doc in enumerate(result['response']['docs'], 1):
                print(f"{i}. ID: {doc['id']} (Score: {doc['score']:.4f})")
                print(f"   Text: {doc['text'][:100]}...")
        
        return result
    
    def test_knn_with_prefiltering(self, query="what is a bank transit number", 
                                   filter_ids=["0", "1", "2", "3", "4"], top_k=3):
        """Test 2: KNN with Pre-filtering"""
        print(f"\n=== Test 2: KNN with Pre-filtering ===")
        print(f"Query: '{query}'")
        print(f"Filter IDs: {filter_ids}")
        print(f"TopK: {top_k}")
        
        # Vectorize query
        vector = self.vectorize_query(query)
        
        # Build KNN query with filter
        filter_query = f"id:({' '.join(filter_ids)})"
        query_data = {
            "query": f"{{!knn f=vector topK={top_k}}}{vector}",
            "filter": filter_query
        }
        
        # Execute query
        result = self.make_request("/select?fl=id,text,score", query_data, 'POST')
        
        if result:
            print(f"Found {result['response']['numFound']} documents")
            for i, doc in enumerate(result['response']['docs'], 1):
                print(f"{i}. ID: {doc['id']} (Score: {doc['score']:.4f})")
                print(f"   Text: {doc['text'][:100]}...")
        
        return result
    
    def test_hybrid_search(self, query="what is a bank transit number", 
                          lexical_field="text", lexical_query="bank", top_k=3):
        """Test 3: Hybrid Search (Dense + Sparse)"""
        print(f"\n=== Test 3: Hybrid Search ===")
        print(f"Neural query: '{query}'")
        print(f"Lexical query: '{lexical_query}' in field '{lexical_field}'")
        print(f"TopK: {top_k}")
        
        # Vectorize query
        vector = self.vectorize_query(query)
        
        # Build hybrid query using boolean query parser
        query_data = {
            "query": {
                "bool": {
                    "should": [
                        f"{{!type=edismax qf={lexical_field} v='{lexical_query}'}}",
                        f"{{!knn f=vector topK={top_k}}}{vector}"
                    ]
                }
            }
        }
        
        # Execute query
        result = self.make_request("/select?fl=id,text,score", query_data, 'POST')
        
        if result:
            print(f"Found {result['response']['numFound']} documents")
            for i, doc in enumerate(result['response']['docs'], 1):
                print(f"{i}. ID: {doc['id']} (Score: {doc['score']:.4f})")
                print(f"   Text: {doc['text'][:100]}...")
        
        return result
    
    def test_reranking_query(self, initial_query="id:(0 1 2 3 4)", 
                           rerank_query="what is a bank transit number", 
                           rerank_docs=4, rerank_weight=1):
        """Test 4: Re-ranking Query"""
        print(f"\n=== Test 4: Re-ranking Query ===")
        print(f"Initial query: '{initial_query}'")
        print(f"Rerank query: '{rerank_query}'")
        print(f"Rerank docs: {rerank_docs}, weight: {rerank_weight}")
        
        # Vectorize reranking query
        vector = self.vectorize_query(rerank_query)
        
        # Build reranking query
        params = {
            'q': initial_query,
            'fl': 'id,text,score',
            'rq': f'{{!rerank reRankQuery=$rqq reRankDocs={rerank_docs} reRankWeight={rerank_weight}}}',
            'rqq': f'{{!knn f=vector topK={rerank_docs}}}{vector}'
        }
        
        # Execute query
        url = f"{self.solr_url}/select"
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            print(f"Error in reranking query: {e}")
            return None
        
        if result:
            print(f"Found {result['response']['numFound']} documents")
            for i, doc in enumerate(result['response']['docs'], 1):
                print(f"{i}. ID: {doc['id']} (Score: {doc['score']:.4f})")
                print(f"   Text: {doc['text'][:100]}...")
        
        return result
    
    def test_solr_health(self):
        """Test Solr health and collection status"""
        print(f"\n=== Solr Health Check ===")
        
        # Ping test
        ping_result = self.make_request("/admin/ping")
        if ping_result:
            print(f"✓ Solr ping successful: {ping_result.get('status')}")
        else:
            print("✗ Solr ping failed")
            return False
        
        # Collection stats
        stats_result = self.make_request("/select?q=*:*&rows=0")
        if stats_result:
            num_docs = stats_result['response']['numFound']
            print(f"✓ Collection has {num_docs} documents")
        else:
            print("✗ Failed to get collection stats")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all neural search tests"""
        print("Starting Neural Search Tests...")
        
        # Health check first
        if not self.test_solr_health():
            print("Solr health check failed. Exiting.")
            return False
        
        # Test queries
        test_queries = [
            "what is a bank transit number",
            "financial institution information",
            "federal tax identification"
        ]
        
        success_count = 0
        total_tests = 0
        
        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Testing with query: '{query}'")
            print(f"{'='*50}")
            
            # Test 1: Basic KNN
            total_tests += 1
            if self.test_basic_knn_query(query):
                success_count += 1
            
            # Test 2: KNN with filtering  
            total_tests += 1
            if self.test_knn_with_prefiltering(query):
                success_count += 1
            
            # Test 3: Hybrid search
            total_tests += 1
            if self.test_hybrid_search(query):
                success_count += 1
            
            # Test 4: Reranking
            total_tests += 1
            if self.test_reranking_query(rerank_query=query):
                success_count += 1
        
        print(f"\n{'='*50}")
        print(f"TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total tests: {total_tests}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_tests - success_count}")
        print(f"Success rate: {(success_count/total_tests)*100:.1f}%")
        
        return success_count == total_tests

def main():
    """Main function to run tests based on command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python neural_search_tester.py <command> [options]")
        print("\nCommands:")
        print("  health              - Check Solr health")
        print("  knn <query>         - Test basic KNN search")
        print("  filter <query>      - Test KNN with filtering")
        print("  hybrid <query>      - Test hybrid search")
        print("  rerank <query>      - Test reranking")
        print("  all                 - Run all tests")
        print("\nExamples:")
        print("  python neural_search_tester.py health")
        print("  python neural_search_tester.py knn 'what is a bank transit number'")
        print("  python neural_search_tester.py all")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    tester = NeuralSearchTester()
    
    if command == 'health':
        tester.test_solr_health()
    
    elif command == 'knn':
        query = sys.argv[2] if len(sys.argv) > 2 else "what is a bank transit number"
        tester.test_basic_knn_query(query)
    
    elif command == 'filter':
        query = sys.argv[2] if len(sys.argv) > 2 else "what is a bank transit number"
        tester.test_knn_with_prefiltering(query)
    
    elif command == 'hybrid':
        query = sys.argv[2] if len(sys.argv) > 2 else "what is a bank transit number"
        tester.test_hybrid_search(query)
    
    elif command == 'rerank':
        query = sys.argv[2] if len(sys.argv) > 2 else "what is a bank transit number"
        tester.test_reranking_query(rerank_query=query)
    
    elif command == 'all':
        tester.run_all_tests()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
