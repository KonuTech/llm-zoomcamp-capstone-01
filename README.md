# Hello there, Traveler. Take a seat and ask about the game you'd like to buy and play..
## Objective

This repository contains the final project for the [LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp) course provided by [DataTalks.Club](https://datatalks.club/).

The primary objective of this project is to apply the knowledge and skills acquired throughout the course. The focus is on constructing a Retrieval-Augmented Generation (RAG) application. In essence, a RAG application enhances the capabilities of pre-trained, widely available language models (LLMs) by incorporating a Knowledge Base (KB). This Knowledge Base acts as a repository of information that the LLM can access whenever a query is made. Essentially, when a query is sent to the LLM, the response is strengthened by the locally maintained Knowledge Base, creating a symbiotic relationship that any organization can cultivate within its own environment.

To build a RAG (Retrieval-Augmented Generation) application, [Elastisearch](https://airflow.apache.org/docs/apache-airflow/stable/index.html) is utilized as the Knowledge Base, providing powerful indexing and search capabilities. For operationalizing the application's usage, a combination of [Flask](https://kafka-python.readthedocs.io/en/master/), [Grafana](https://spark.apache.org/docs/latest/api/python/index.html), and [PostgreSQL](https://www.postgresql.org/) is employed. Flask serves as the backend framework, handling the API endpoints and routing requests, while Grafana is used for monitoring and visualizing system metrics, ensuring smooth performance and quick identification of issues. PostgreSQL functions as the database solution for storing and managing user activities, including feedback on whether the answers provided by the RAG application were meaningful. This enables reliable and efficient data persistence, ensuring that all interactions and feedback are recorded and easily accessible for future analysis. The integrated stack ensures that the application remains maintainable, delivering a comprehensive solution for handling RAG-based queries.

 
The architectural overview of the project is depicted in the diagram below, providing a high-level perspective of the system's design and interactions.

![Architecture Diagram](images/rag.svg)


## Peer review criterias - a self assassment:

* Problem description
    * 0 points: The problem is not described
    * 1 point: The problem is described but briefly or unclearly
    * 2 points: The problem is well-described and it's clear what problem the project solves
* RAG flow
    * 0 points: No knowledge base or LLM is used
    * 1 point: No knowledge base is used, and the LLM is queried directly
    * 2 points: Both a knowledge base and an LLM are used in the RAG flow 
* Retrieval evaluation
    * 0 points: No evaluation of retrieval is provided
    * 1 point: Only one retrieval approach is evaluated
    * 2 points: Multiple retrieval approaches are evaluated, and the best one is used
* RAG evaluation
    * 0 points: No evaluation of RAG is provided
    * 1 point: Only one RAG approach (e.g., one prompt) is evaluated
    * 2 points: Multiple RAG approaches are evaluated, and the best one is used
* Interface
   * 0 points: No way to interact with the application at all
   * 1 point: Command line interface, a script, or a Jupyter notebook
   * 2 points: UI (e.g., Streamlit), web application (e.g., Django), or an API (e.g., built with FastAPI) 
* Ingestion pipeline
   * 0 points: No ingestion
   * 1 point: Semi-automated ingestion of the dataset into the knowledge base, e.g., with a Jupyter notebook
   * 2 points: Automated ingestion with a Python script or a special tool (e.g., Mage, dlt, Airflow, Prefect)
* Monitoring
   * 0 points: No monitoring
   * 1 point: User feedback is collected OR there's a monitoring dashboard
   * 2 points: User feedback is collected and there's a dashboard with at least 5 charts
* Containerization
    * 0 points: No containerization
    * 1 point: Dockerfile is provided for the main application OR there's a docker-compose for the dependencies only
    * 2 points: Everything is in docker-compose
* Reproducibility
    * 0 points: No instructions on how to run the code, the data is missing, or it's unclear how to access it
    * 1 point: Some instructions are provided but are incomplete, OR instructions are clear and complete, the code works, but the data is missing
    * 2 points: Instructions are clear, the dataset is accessible, it's easy to run the code, and it works. The versions for all dependencies are specified.
* Best practices
    * [ ] Hybrid search: combining both text and vector search (at least evaluating it) (1 point)
    * [ ] Document re-ranking (1 point)
    * [ ] User query rewriting (1 point)
* Bonus points (not covered in the course)
    * [ ] Deployment to the cloud (2 points)
    * [ ] Up to 3 extra bonus points if you want to award for something extra (write in feedback for what)
