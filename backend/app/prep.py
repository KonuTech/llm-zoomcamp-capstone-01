import os
import json
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, ConnectionError
from dotenv import load_dotenv
from ingest import ingest_documents  # Keep this import as it triggers the ingest.py script
from db import init_db

load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL", "http://elasticsearch:9200")
INDEX_NAME = os.getenv("INDEX_NAME", "reviews-steam")

def check_elasticsearch_connection(es_client):
    """Check if the Elasticsearch server is available."""
    try:
        if es_client.ping():
            print("Connected to Elasticsearch")
            return True
        else:
            print("Could not connect to Elasticsearch")
            return False
    except ConnectionError as e:
        print(f"Connection error: {e}")
        return False

def setup_elasticsearch():
    """Setup Elasticsearch index with the specified settings and mappings."""
    print("Setting up Elasticsearch...")
    es_client = Elasticsearch(ELASTIC_URL)

    # Check Elasticsearch connection
    if not check_elasticsearch_connection(es_client):
        print("Exiting: Elasticsearch is not available.")
        return None  # Indicate that the setup failed

    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "appid": {"type": "keyword"},
                "timestamp_query": {"type": "integer"},
                "title": {"type": "keyword"},
                "author.steamid": {"type": "keyword"},
                "author.playtimeforever": {"type": "integer"},
                "author.playtime_last_two_weeks": {"type": "integer"},
                "author.playtime_at_review": {"type": "integer"},
                "author.last_played": {"type": "integer"},
                "language": {"type": "keyword"},
                "review": {"type": "text"},
                "voted_up": {"type": "boolean"},
                "votes_up": {"type": "integer"},
                "timestamp_created": {"type": "integer"},
                "timestamp_updated": {"type": "integer"},
                "question": {"type": "text"},
                "answer": {"type": "text"},
                "section": {"type": "keyword"},
                "question_vector": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                },
                "answer_vector": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                },
                "question_answer_vector": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                },
            }
        }
    }

    # Delete existing index if it exists
    try:
        es_client.indices.delete(index=INDEX_NAME, ignore_unavailable=True)
        print(f"Deleted index: {INDEX_NAME}")
    except NotFoundError:
        print(f"Index {INDEX_NAME} not found, nothing to delete")

    # Create new index
    es_client.indices.create(index=INDEX_NAME, settings=index_settings['settings'], mappings=index_settings['mappings'])
    print(f"Created index: {INDEX_NAME}")

    return es_client

def load_documents(file_path):
    """Load documents from the specified JSON file."""
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        documents = json.load(jsonfile)
    return documents

def index_documents(es_client, documents):
    """Index documents into Elasticsearch."""
    print("Indexing documents...")
    for doc in documents:
        es_client.index(index=INDEX_NAME, document=doc)
    print(f"Indexed {len(documents)} documents")

    # Refresh the index to make the documents available for search
    es_client.indices.refresh(index=INDEX_NAME)
    print("Index refreshed")

def main():
    print("Starting the indexing process...")

    # Path to the ground-truth-retrieval.json file
    json_file_path = os.path.abspath('../llm-zoomcamp-capstone-01/backend/app/data/ground_truth_retrieval.json')

    # Check if the ground_truth_retrieval.json file exists and is not empty
    if os.path.exists(json_file_path):
        file_size = os.path.getsize(json_file_path)
        if file_size > 0:
            print(f"Found existing data in {json_file_path} (size: {file_size} bytes). Skipping ingesting documents.")
        else:
            print(f"Found existing empty data in {json_file_path}. Running ingest_documents...")
            data_directory = os.path.abspath('../llm-zoomcamp-capstone-01/backend/app/data/reviews')
            ingest_documents(data_directory)
    else:
        print(f"No data found in {json_file_path}. Running ingest_documents...")
        data_directory = os.path.abspath('../llm-zoomcamp-capstone-01/backend/app/data/reviews')
        ingest_documents(data_directory)

    if not os.path.exists(json_file_path):
        print(f"Error: ground_truth_retrieval.json not found at {json_file_path}")
        return

    print(f"Loading documents from {json_file_path}...")
    documents = load_documents(json_file_path)
    print(f"Total documents loaded: {len(documents)}")

    es_client = setup_elasticsearch()
    if es_client is None:
        print("Failed to set up Elasticsearch. Exiting.")
        return

    index_documents(es_client, documents)

    print("Initializing database...")
    init_db()

    print("Indexing process completed successfully!")

if __name__ == "__main__":
    main()
