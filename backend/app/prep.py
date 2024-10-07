import os
import json
from elasticsearch import Elasticsearch, NotFoundError, ConnectionError
from dotenv import load_dotenv
from ingest import ingest_documents  # Keep this import as it triggers the ingest.py script
from db import init_db
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import numpy as np

load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")  # Changed to localhost for local testing
INDEX_NAME = os.getenv("INDEX_NAME", "reviews-steam")

class ReviewIndexer:
    def __init__(self, es_host=ELASTIC_URL, index_name=INDEX_NAME, model=None):
        print("Initializing ReviewIndexer...")
        self.es = Elasticsearch([es_host])
        self.index_name = index_name
        self.model = model  # Expecting a SentenceTransformer model to encode text
        
        # Check the connection upon initialization
        self.check_connection()
        
        self.index_settings = {
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

        # Drop the index if it exists and create a new one
        self.drop_and_create_index()

    def check_connection(self):
        """Check if Elasticsearch connection is established."""
        try:
            print("Checking connection to Elasticsearch...")
            self.es.ping()
            print("Connected to Elasticsearch!")
        except ConnectionError:
            print("Failed to connect to Elasticsearch.")

    def drop_and_create_index(self):
        """Delete the existing index if it exists and create a new one."""
        try:
            print(f"Checking if index '{self.index_name}' exists...")
            if self.es.indices.exists(index=self.index_name):
                print(f"Index '{self.index_name}' exists. Deleting it...")
                self.es.indices.delete(index=self.index_name)
                print(f"Index '{self.index_name}' deleted.")
            print(f"Creating index '{self.index_name}'...")
            self.es.indices.create(index=self.index_name, body=self.index_settings)  # Update to `body` since the settings are not expected to change.
            print(f"Index '{self.index_name}' created.")
        except Exception as e:
            print(f"Error creating index: {e}")

    def encode_vectors(self, question, answer):
        """Generate vectors for question, answer, and a combined question + answer."""
        print("Encoding vectors for question and answer...")
        # Use float64 to avoid np.float_ deprecation
        question_vector = self.model.encode(question, convert_to_numpy=True).astype(np.float64) if question else np.zeros(384, dtype=np.float64)
        answer_vector = self.model.encode(answer, convert_to_numpy=True).astype(np.float64) if answer else np.zeros(384, dtype=np.float64)
        combined_text = f"{question} {answer}" if question and answer else ""
        question_answer_vector = self.model.encode(combined_text, convert_to_numpy=True).astype(np.float64) if combined_text else np.zeros(384, dtype=np.float64)
        print("Vector encoding complete.")
        return question_vector.tolist(), answer_vector.tolist(), question_answer_vector.tolist()

    def prepare_document(self, review):
        """Prepare the document to be indexed."""
        print(f"Preparing document for appid {review['appid']}...")
        question_vector, answer_vector, question_answer_vector = self.encode_vectors(review["question"], review["answer"])
        
        return {
            "appid": review["appid"],
            "timestamp_query": review["review"]["timestamp_query"],
            "title": review["review"]["title"],
            "author.steamid": review["review"]["author.steamid"],
            "author.playtimeforever": review["review"]["author.playtimeforever"],
            "author.playtime_last_two_weeks": review["review"]["author.playtime_last_two_weeks"],
            "author.playtime_at_review": review["review"]["author.playtime_at_review"],
            "author.last_played": review["review"]["author.last_played"],
            "language": review["review"]["language"],
            "review": review["review"]["review"],
            "voted_up": review["review"]["voted_up"],
            "votes_up": review["review"]["votes_up"],
            "timestamp_created": review["review"]["timestamp_created"],
            "timestamp_updated": review["review"]["timestamp_updated"],
            "question": review["question"],
            "answer": review["answer"],
            "section": review["section"],
            "question_vector": question_vector,
            "answer_vector": answer_vector,
            "question_answer_vector": question_answer_vector
        }

    def index_reviews(self, reviews):
        """Index the provided reviews into Elasticsearch."""
        print(f"Starting indexing of {len(reviews)} reviews...")
        for review in tqdm(reviews):
            # Prepare the document
            doc = self.prepare_document(review)

            # Index the document
            try:
                print(f"Indexing document for appid {review['appid']}...")
                self.es.index(index=self.index_name, document=doc)  # Change here from body to document
                print(f"Document for appid {review['appid']} indexed successfully.")
            except Exception as e:
                print(f"Error indexing document with appid {review['appid']}: {e}")

    def load_reviews_from_file(self, file_path):
        """Load reviews from a JSON file."""
        print(f"Loading reviews from file: {file_path}")
        try:
            with open(file_path, 'r') as file:
                reviews = json.load(file)
                print(f"Loaded {len(reviews)} reviews.")
                return reviews
        except Exception as e:
            print(f"Error loading reviews from file: {e}")
            return []

# Example usage
if __name__ == "__main__":
    # Define the data directory and output file path
    data_dir = os.path.abspath('../reviews-assistant/data/ground_truth')
    output_file = os.path.join(data_dir, "ground_truth_retrieval.json")

    # Initialize the model
    print("Initializing SentenceTransformer model...")
    model_name = 'multi-qa-MiniLM-L6-cos-v1'
    model = SentenceTransformer(model_name)
    print(f"Model '{model_name}' initialized.")

    # Load reviews from the specified JSON file
    indexer = ReviewIndexer(model=model)

    # Initialize paths
    json_file_path = os.path.abspath('../llm-zoomcamp-capstone-01/backend/app/data/ground_truth_retrieval.json')

    # Check if the file exists and print its size
    if os.path.exists(json_file_path):
        file_size = os.path.getsize(json_file_path)
        print(f"Found existing data in {json_file_path} (size: {file_size} bytes).")
        if file_size > 0:
            print("Loading reviews from existing file...")
            reviews = indexer.load_reviews_from_file(json_file_path)
            if reviews:
                indexer.index_reviews(reviews)
            else:
                print("No reviews found to index.")
        else:
            print(f"Found existing empty data in {json_file_path}. Running ingest_documents...")
            data_directory

    print("Initializing PostgreSQL database...")
    init_db()
