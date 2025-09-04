# Solr-neural-search
A comprehensive Docker-based Apache Solr neural search application Bloomberg Terminal style

# Apache Solr Neural Search Implementation

This project implements neural search functionality in Apache Solr 9.4.1 using Docker, based on the [Sease tutorial](https://sease.io/2023/01/apache-solr-neural-search-tutorial.html). It provides a complete end-to-end implementation with vector generation, document indexing, and comprehensive testing of all neural search methods.

## Features

- 🚀 **Docker-based setup** with Solr 9.4.1
- 🧠 **Vector embeddings** using SentenceTransformers (all-MiniLM-L6-v2)
- 🔍 **Complete neural search methods**:
  - Basic KNN queries
  - KNN with pre-filtering
  - Hybrid search (dense + sparse)
  - Query re-ranking
- 🧪 **Comprehensive testing scripts**
- 📊 **Sample data generation**
- 🔧 **Easy setup and configuration**

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local script execution)
- At least 4GB RAM available for Docker

### 1. Clone and Setup

```bash
# Create project directory
mkdir solr-neural-search
cd solr-neural-search

# Save all the provided files in their respective locations
# (docker-compose.yml, Dockerfile, requirements.txt, etc.)
```

### 2. Project Structure

```
solr-neural-search/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── Readme.md
├── setup.sh
├── configs/
│   ├── solrconfig.xml
│   ├── schema.xml
│   ├── stopwords.txt
│   └── synonyms.txt
├── scripts/
│   ├── sample_data_generator.py
│   ├── vector_generation.py
│   ├── document_indexing.py
│   ├── query_vectorizer.py
│   └── neural_search_tester.py
└── data/
    └── (generated data files)
```

### 3. One-Command Setup

```bash
# Make setup script executable
chmod +x setup.sh

# Run complete setup
./setup.sh setup
```

This will:
- Start Solr container
- Create the neural search collection
- Generate sample data
- Create vector embeddings
- Index documents
- Run comprehensive tests

### 4. Access Solr

- **Solr Admin UI**: http://localhost:8983/solr/
- **Collection**: ms-marco

## Manual Usage

### Individual Commands

```bash
# Start services only
./setup.sh start

# Generate sample data
./setup.sh generate-data

# Generate vectors
./setup.sh generate-vectors

# Index documents
./setup.sh index

# Run tests
./setup.sh test

# Stop services
./setup.sh stop
```

### Using Docker Exec

```bash
# Execute scripts inside the container
docker exec -it $(docker ps -qf 'name=neural-search-app') python scripts/neural_search_tester.py health

# Run specific test
docker exec -it $(docker ps -qf 'name=neural-search-app') python scripts/neural_search_tester.py knn "what is a bank number"

# Generate custom vectors
docker exec -it $(docker ps -qf 'name=neural-search-app') python scripts/query_vectorizer.py "your query here"
```

## Neural Search Methods Implemented

### 1. Basic KNN Query

```python
# Test basic vector similarity search
python scripts/neural_search_tester.py knn "what is a bank transit number"
```

### 2. KNN with Pre-filtering

```python
# Search within a subset of documents
python scripts/neural_search_tester.py filter "federal tax number"
```

### 3. Hybrid Search (Dense + Sparse)

```python
# Combine neural and lexical search
python scripts/neural_search_tester.py hybrid "bank routing information"
```

### 4. Query Re-ranking

```python
# Re-rank results using neural similarity
python scripts/neural_search_tester.py rerank "financial institution"
```

## Configuration Details

### Solr Schema

The schema includes:
- **DenseVectorField** with 384 dimensions (matching all-MiniLM-L6-v2)
- **Cosine similarity** function
- **HNSW algorithm** for efficient vector indexing

### Vector Model

- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Dimensions**: 384
- **Type**: BERT-based sentence transformer
- **Size**: ~80MB

### Sample Data

The project includes 20 sample documents covering:
- Financial/banking information
- Tax identification numbers
- General knowledge topics
- Technical/AI-related content

## API Examples

### Basic KNN Search

```bash
curl -X POST http://localhost:8983/solr/ms-marco/select \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{!knn f=vector topK=3}[-0.01, 0.02, ...]",
    "fl": "id,text,score"
  }'
```

### Hybrid Search

```bash
curl -X POST http://localhost:8983/solr/ms-marco/select \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "should": [
          "{!type=edismax qf=text v=\"bank\"}",
          "{!knn f=vector topK=3}[-0.01, 0.02, ...]"
        ]
      }
    }
  }'
```

## Troubleshooting

### Common Issues

1. **Solr not starting**:
   ```bash
   docker logs $(docker ps -qf 'name=solr')
   ```

2. **Python dependencies**:
   ```bash
   docker exec -it $(docker ps -qf 'name=neural-search-app') pip install -r requirements.txt
   ```

3. **Collection not found**:
   ```bash
   docker exec -it $(docker ps -qf 'name=solr') solr create -c ms-marco
   ```

4. **Permission errors**:
   ```bash
   sudo chown -R $(whoami):$(whoami) solr-data/
   ```

### Performance Tuning

- **Increase JVM heap**: Modify `SOLR_HEAP` in docker-compose.yml
- **Adjust HNSW parameters**: Modify `schema.xml` vector field configuration
- **Batch size**: Adjust `BATCH_SIZE` in indexing scripts

## Development

### Adding Custom Data

1. Replace sample data in `scripts/sample_data_generator.py`
2. Or provide your own files:
   ```bash
   python scripts/vector_generation.py your_docs.txt your_vectors.txt
   python scripts/document_indexing.py your_docs.txt your_vectors.txt
   ```

### Custom Queries

```bash
# Vectorize any query
python scripts/query_vectorizer.py "your custom query"

# Use in search
python scripts/neural_search_tester.py knn "your custom query"
```

### Extending Tests

Modify `scripts/neural_search_tester.py` to add:
- Custom similarity functions
- Different vector models
- Advanced filtering logic
- Performance benchmarks

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Text Corpus   │───▶│ Vector Embeddings│
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Solr Indexing  │◀───│  Neural Search  │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ Document Store  │───▶│  Query Results  │
└─────────────────┘    └─────────────────┘
```

## References

- [Sease Neural Search Tutorial](https://sease.io/2023/01/apache-solr-neural-search-tutorial.html)
- [Apache Solr Dense Vector Search](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html)
- [SentenceTransformers Documentation](https://www.sbert.net/)
- [MS MARCO Dataset](https://microsoft.github.io/msmarco/)

## License

This project is provided as-is for educational and testing purposes. Please refer to individual component licenses (Apache Solr, SentenceTransformers, etc.) for production use.
