#!/bin/bash

# Solr Neural Search Setup and Testing Script
# Based on the Sease tutorial implementation

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOLR_URL="http://localhost:8983/solr/ms-marco"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

wait_for_solr() {
    print_status "Waiting for Solr to be ready..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$SOLR_URL/admin/ping" > /dev/null 2>&1; then
            print_success "Solr is ready!"
            return 0
        fi
        attempt=$((attempt + 1))
        print_status "Attempt $attempt/$max_attempts - Solr not ready yet, waiting..."
        sleep 5
    done
    
    print_error "Solr failed to start within expected time"
    return 1
}

setup_directories() {
    print_status "Setting up directories..."
    mkdir -p data
    mkdir -p scripts
    mkdir -p configs
    mkdir -p solr-data
}

generate_sample_data() {
    print_status "Generating sample data..."
    python3 scripts/sample_data_generator.py
}

generate_vectors() {
    print_status "Generating vector embeddings..."
    python3 scripts/vector_generation.py data/sample_documents.tsv data/sample_vectors.tsv
}

index_documents() {
    print_status "Indexing documents into Solr..."
    SOLR_URL="$SOLR_URL" python3 scripts/document_indexing.py data/sample_documents.tsv data/sample_vectors.tsv
}

run_tests() {
    print_status "Running neural search tests..."
    SOLR_URL="$SOLR_URL" python3 scripts/neural_search_tester.py all
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        return 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        return 1
    fi
    
    print_success "Docker and Docker Compose are available"
}

start_services() {
    print_status "Starting Docker services..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    print_success "Services started"
}

stop_services() {
    print_status "Stopping Docker services..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    print_success "Services stopped"
}

full_setup() {
    print_status "Starting full neural search setup..."
    
    # Check prerequisites
    check_docker
    
    # Setup directories
    setup_directories
    
    # Start services
    start_services
    
    # Wait for Solr
    wait_for_solr
    
    # Generate sample data
    generate_sample_data
    
    # Generate vectors
    generate_vectors
    
    # Index documents
    index_documents
    
    # Run tests
    run_tests
    
    print_success "Full setup completed successfully!"
    print_status "You can now:"
    print_status "- Access Solr Admin UI: http://localhost:8983/solr/"
    print_status "- Run individual tests: docker exec -it \$(docker ps -qf 'name=neural-search-app') python scripts/neural_search_tester.py <command>"
    print_status "- View logs: docker logs \$(docker ps -qf 'name=solr')"
}

show_help() {
    cat << EOF
Solr Neural Search Setup Script

Usage: $0 <command>

Commands:
    setup           Run full setup (start services, generate data, index, test)
    start           Start Docker services only
    stop            Stop Docker services
    generate-data   Generate sample documents
    generate-vectors Generate vector embeddings
    index          Index documents into Solr
    test           Run neural search tests
    help           Show this help message

Examples:
    $0 setup                    # Full setup from scratch
    $0 start                    # Just start the services
    $0 test                     # Run tests (after setup)
    $0 stop                     # Stop all services

Environment Variables:
    SOLR_URL                    Solr endpoint (default: http://localhost:8983/solr/ms-marco)

EOF
}

# Main script logic
case "${1:-help}" in
    setup)
        full_setup
        ;;
    start)
        check_docker
        start_services
        wait_for_solr
        ;;
    stop)
        stop_services
        ;;
    generate-data)
        generate_sample_data
        ;;
    generate-vectors)
        generate_vectors
        ;;
    index)
        index_documents
        ;;
    test)
        run_tests
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
