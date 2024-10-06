import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch, ConnectionError, NotFoundError
from dotenv import load_dotenv


load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")  # Changed to localhost for local testing
INDEX_NAME = os.getenv("INDEX_NAME", "reviews-steam")

class ReviewReader:
    def __init__(self, es_host=ELASTIC_URL, index_name=INDEX_NAME, model=None):
        self.es = Elasticsearch([es_host])
        self.index_name = index_name
        self.model = model  # SentenceTransformer model for embedding generation

        # Check the connection on initialization
        self.check_connection()

    def check_connection(self):
        """Check if Elasticsearch connection is established."""
        try:
            print("Checking connection to Elasticsearch...")
            self.es.ping()
            print("Connected to Elasticsearch!")
        except ConnectionError:
            print("Failed to connect to Elasticsearch.")
    
    def read_all_reviews(self):
        """Retrieve all reviews from the index."""
        try:
            response = self.es.search(index=self.index_name, query={"match_all": {}})
            return response['hits']['hits']  # returns the list of documents
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

    def read_review_by_appid(self, appid):
        """Retrieve reviews by appid."""
        try:
            response = self.es.search(index=self.index_name, query={
                "term": {"appid": appid}
            })
            return response['hits']['hits']  # list of documents matching the appid
        except Exception as e:
            print(f"Error retrieving document with appid {appid}: {e}")
            return []

    def read_reviews_knn(self, query, title, vector_field="answer_vector", num_results=5):
        """Retrieve reviews using KNN search to find similar vectors."""
        try:
            if self.model is None:
                raise ValueError("Model for embedding generation is not initialized.")

            # Generate embedding vector from the query
            knn_vector = self.model.encode(query).tolist()

            # Define the KNN query
            knn_query = {
                "knn": {
                    "field": vector_field,
                    "query_vector": knn_vector,
                    "k": num_results,
                    "num_candidates": 10000,
                    "filter": {
                        "term": {"title": title}
                    }
                }
            }

            # Execute the search
            es_results = self.es.search(index=self.index_name, query=knn_query)
            return [hit['_source'] for hit in es_results['hits']['hits']]
        
        except Exception as e:
            print(f"Error executing KNN search: {e}")
            return []

    def read_reviews_knn_and_keyword(self, field, query, vector, title, num_results=5):
        """Retrieve reviews using both KNN and keyword search."""
        try:
            if self.model is None:
                raise ValueError("Model for embedding generation is not initialized.")

            # Define the KNN part of the query
            knn_query = {
                "knn": {
                    "field": field,
                    "query_vector": vector,
                    "k": num_results,
                    "num_candidates": 10000,
                    "filter": {
                        "term": {"title": title}
                    }
                }
            }

            # Define the keyword search part of the query
            keyword_query = {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": ["question^3", "answer", "section"],
                            "type": "best_fields"
                        }
                    },
                    "filter": {
                        "term": {"title": title}
                    }
                }
            }

            # Combine the KNN and keyword search
            combined_query = {
                "knn": knn_query["knn"],
                "query": keyword_query
            }

            # Execute the search
            es_results = self.es.search(index=self.index_name, query=combined_query, size=num_results)
            return [hit['_source'] for hit in es_results['hits']['hits']]

        except Exception as e:
            print(f"Error executing combined KNN and keyword search: {e}")
            return []

    def read_reviews_knn_and_keyword_rrf(self, field, query, vector, title, k=60, num_results=5):
        """Retrieve reviews using both KNN and keyword search with RRF."""
        try:
            if self.model is None:
                raise ValueError("Model for embedding generation is not initialized.")

            # Define the KNN query
            knn_query = {
                "knn": {
                    "field": field,
                    "query_vector": vector,
                    "k": num_results,
                    "num_candidates": 10000,
                    "filter": {
                        "term": {"title": title}
                    }
                }
            }

            # Define the keyword search query
            keyword_query = {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": ["question", "answer", "section"],
                            "type": "best_fields"
                        }
                    },
                    "filter": {"term": {"title": title}}
                }
            }

            # Execute the KNN and keyword searches
            knn_results = self.es.search(index=self.index_name, query=knn_query, size=num_results)['hits']['hits']
            keyword_results = self.es.search(index=self.index_name, query=keyword_query, size=num_results)['hits']['hits']

            # Compute RRF scores and rerank the results
            rrf_scores = {}
            for rank, hit in enumerate(knn_results):
                doc_id = hit['_id']
                rrf_scores[doc_id] = self.compute_rrf(rank + 1, k)

            for rank, hit in enumerate(keyword_results):
                doc_id = hit['_id']
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + self.compute_rrf(rank + 1, k)

            # Sort documents based on RRF scores
            reranked_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

            # Return the top reranked documents
            return [self.es.get(index=self.index_name, id=doc_id)['_source'] for doc_id, _ in reranked_docs[:num_results]]

        except Exception as e:
            print(f"Error executing KNN and keyword search with RRF: {e}")
            return []

    def compute_rrf(self, rank, k=60):
        """Compute Reciprocal Rank Fusion (RRF) score."""
        return 1 / (k + rank)
