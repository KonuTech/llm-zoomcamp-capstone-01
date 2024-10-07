import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from read import ReviewReader


load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")  # Changed to localhost for local testing
INDEX_NAME = os.getenv("INDEX_NAME", "reviews-steam")

def check_index_mapping(es_host=ELASTIC_URL, index_name=INDEX_NAME):
    es = Elasticsearch([es_host])

    try:
        # Get the index mappings
        response = es.indices.get_mapping(index=index_name)
        mapping = response[index_name]['mappings']
        
        # Check for vector fields and their dimensions
        vector_fields = ["question_vector", "answer_vector", "question_answer_vector"]
        
        for field in vector_fields:
            if field in mapping['properties']:
                dims = mapping['properties'][field]['dims']
                print(f"{field}: {dims} dimensions")
            else:
                print(f"{field} not found in index.")
    except Exception as e:
        print(f"Error retrieving index mapping: {e}")


def check_vector_dimensions(query, model_name='multi-qa-MiniLM-L6-cos-v1'):
    # Load the model
    model = SentenceTransformer(model_name)

    # Encode the query and get the vector
    vector = model.encode(query, clean_up_tokenization_spaces=False)

    # Check the dimensions of the vector
    vector_dimensions = len(vector)
    print(f"Generated vector has {vector_dimensions} dimensions.")


def verify_appid_exists(es_host=ELASTIC_URL, index_name=INDEX_NAME, appid=None):
    es = Elasticsearch([es_host])

    try:
        # Define a query to check if the appid exists
        search_query = {
            "query": {
                "term": {
                    "appid": appid  # Filter by appid
                }
            }
        }

        # Perform the search
        es_results = es.search(index=index_name, body=search_query)

        if es_results['hits']['total']['value'] > 0:
            print(f"AppID '{appid}' exists in the index.")
            for hit in es_results['hits']['hits']:
                print(hit['_id'])
        else:
            print(f"AppID '{appid}' not found in the index.")

    except Exception as e:
        print(f"Error checking for AppID: {e}")

def read_ids(limit=10):  # Add a limit parameter with a default value
    model_name = 'multi-qa-MiniLM-L6-cos-v1'
    model = SentenceTransformer(model_name)

    # Create a reader instance with the model
    reader = ReviewReader(model=model)

    # Example of reading all indexed reviews
    all_reviews = reader.read_all_reviews()

    print(f"First {limit} Indexed Reviews:")
    for review in all_reviews[:limit]:  # Limit the number of returned reviews
        print(review['_id'])

if __name__ == "__main__":
    # Run the check
    check_index_mapping()
    # Example Usage
    query = 'Is God of War: Ragnarok a game for kids?'
    check_vector_dimensions(query)
    verify_appid_exists(appid="2322010")
    read_ids(limit=3)
