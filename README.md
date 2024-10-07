# Hello there, Traveler. Take a seat and ask about the game you'd like..
## The Quest

This repository contains the final project for the [LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp) course provided by [DataTalks.Club](https://datatalks.club/).

The primary objective of this project is to apply the knowledge and skills acquired throughout the course. The focus is on constructing a Retrieval-Augmented Generation (RAG) application, which will enhance the generative capabilities of a selected LLM in providing answers to user queries about computer games. For example, if a new game like God of War: Ragnarok has just been released, a user might ask our RAG application for opinions about the game's general state. Based on the responses, the user could decide whether to buy the game immediately or wait until the price drops or bugs from the initial release are fixed.

## The Landscape
In essence, a RAG application enhances the capabilities of pre-trained, widely available language models (LLMs) by incorporating a Knowledge Base (KB). This Knowledge Base acts as a repository of information that the LLM can access whenever a query is made. Essentially, when a query is sent to the LLM, the response is strengthened by the locally maintained Knowledge Base, creating a symbiotic relationship that any organization can cultivate within its own environment.

To build a RAG (Retrieval-Augmented Generation) application, [Elastisearch](https://www.elastic.co/docs) is utilized as the Knowledge Base, providing powerful indexing and search capabilities. For operationalizing the application's usage, a combination of [Flask](https://flask.palletsprojects.com/en/3.0.x/), [Grafana](https://grafana.com/docs/grafana/latest/), and [PostgreSQL](https://www.postgresql.org/) is employed. Flask serves as the backend framework, handling the API endpoints and routing requests, while Grafana is used for monitoring and visualizing system metrics, ensuring smooth performance and quick identification of issues. PostgreSQL functions as the database solution for storing and managing user activities, including feedback on whether the answers provided by the RAG application were meaningful. This enables reliable and efficient data persistence, ensuring that all interactions and feedback are recorded and easily accessible for future analysis. The integrated stack ensures that the application remains maintainable, delivering a comprehensive solution for handling RAG-based queries.

## The Lore
The architectural overview of the project is depicted in the diagram below, providing a high-level perspective of the system's design and interactions.

![Architecture Diagram](images/rag.svg)



### Applied Technologies

| Name                   | Scope                                       | Description                                                                                                         |
| ----------------------| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| Docker Desktop         | Continuous integration, local development, containerization | Docker Desktop is a platform that enables the development, shipping, and running of applications within containers.  |
| Jupyter Lab            | Interactive computing, data analysis       | Jupyter Lab is an open-source web application that provides a flexible interface for working with Jupyter notebooks, code, and data, making it ideal for interactive computing and data analysis. |
| Elasticsearch         | Search engine, analytics                   | Elasticsearch is a distributed search and analytics engine built on Apache Lucene, designed for horizontal scalability, reliability, and real-time search capabilities. |
| Flask                  | Web framework                              | Flask is a lightweight WSGI web application framework for Python that provides the tools and libraries to build web applications quickly and with minimal overhead. |
| Grafana                | Monitoring, visualization                  | Grafana is an open-source platform for monitoring and observability that allows users to visualize metrics from various data sources through customizable dashboards. |
| PostgreSQL             | RDBMS                                      | PostgreSQL is an open-source relational database management system (RDBMS) known for its reliability, robustness, and extensive feature set, commonly used for storing structured data. |
| Pipenv                 | Dependency management                      | Pipenv is a tool that simplifies dependency management for Python projects by creating a virtual environment and managing package installations in a unified manner. |
| OpenAI ChatGPT-4 Mini | Natural language processing, conversational AI | OpenAI ChatGPT-4 Mini is a smaller, optimized version of the ChatGPT model designed for generating human-like text responses in conversational contexts. |



## How to kill a dragon each time the same way
### Pre-requisties

* Python 3.10 or above
* Docker Desktop
* allowed virtualization in BIOS

### Project Setup Guidelines

To ensure reproducibility and set up your project environment, follow these guidelines:


0. **Clone the Repository**:

To clone the repository, run the following command:

```bash
git clone https://github.com/dimzachar/Parthenon-RAG-Game.git
cd Parthenon-RAG-Game
```
1. **Clone the Repository**:
To configure the environment, execute:

```bash
cp .envrc_template .env
```
Alternatively, you can rename `.envrc_template` in the root directory to `.env`.

Key Environment Variables:

- **ELASTIC_URL**: Elasticsearch connection URL
- **POSTGRES_DB**, **POSTGRES_USER**, **POSTGRES_PASSWORD**: PostgreSQL connection details
- **OPENAI_API_KEY**: Your OpenAI API key for LLM interactions
- **INDEX_NAME**: Name of the Elasticsearch index for the knowledge base

Make sure to replace `YOUR_KEY` with your OpenAI API key.

2. **Virtual Environment Setup**:
   - Create a virtual environment named `.venv` using Python's built-in `venv` module:
     ```
     python3 -m venv .venv
     ```
   - Activate the virtual environment using the appropriate command based on your operating system:
     - For Windows:
       ```
       source .venv/Scripts/activate
       ```
     - For Unix/Mac:
       ```
       source .venv/bin/activate
       ```

3. **Upgrade Pip**:
   - Ensure you have the latest version of pip installed within the virtual environment:
     ```
     python -m pip install --upgrade pip
     ```

4. **Install Project Dependencies with Pipenv**:
   - First, ensure that **Pipenv** is installed. If you haven't installed it yet, you can do so by running the following command:
     ```
     pip install pipenv
     ```
   - Navigate to project directory where the `Pipfile` is located. Start a new Pipenv environment or activate an existing one, run:
     ```
     pipenv shell
     ```
   - Finally, install the project dependencies listed in the `Pipfile` by executing (yes, it takes a while):
     ```
     pipenv install
     ```

5. **Docker Setup**:
   - Next, build the containerized apps, namely: Flask, Elasticsearch, PostgreSQL, and Grafana by running below command (yes, this will also take a while).
     ```
     docker-compose build
     ```
   - Start Dockerized apps:
     ```
     docker-compose up
     ```
6. **Inexing Steam reviews**:
We can now start indexing the pre-downloaded Steam reviews with Elasticsearch:
     ```
     python3 backend/app/prep.py
     ```
Again, this process will take a while. As feedback, you will encounter a lot of output log being printed to your terminal.


If you would like to see how the reviews were downloaded, please check the [notebook](https://github.com/KonuTech/llm-zoomcamp-capstone-01/blob/main/notebooks/001_rag_test_002.ipynb). There, you will find the `SteamReviewFetcher` class.


7. **Grafana**:
    - For monitoring purposes, we can import a pre-built Grafana dashboard by running a script located at `./grafana/init.py`. First, ensure the `POSTGRES_HOST` environment variable is set to `postgres`:
      ```
      echo $POSTGRES_HOST
      export POSTGRES_HOST=postgres
      cd grafana
      python init.py
      ```
    - Start Grafana at `http://localhost:3000/` and skip creation of a user.
    The initial view of Grafana dashboard after initialization looks like on below screen shot:

<img src="images/01.png" width="60%"/>


### Check if everything works as intended: 

Please use the screenshots below to visually validate if all of the steps/processes are working fine.


<img src="static/docker_01.jpg" width="60%"/>



## Peer review criterias - a self assassment:

* Problem description
    * 2 points: The problem is well-described and it's clear what problem the project solves
* RAG flow
    * 2 points: Both a knowledge base and an LLM are used in the RAG flow 
* Retrieval evaluation
    * 1 point: Only one retrieval approach is evaluated
* RAG evaluation
    * 1 point: Only one RAG approach (e.g., one prompt) is evaluated
* Interface
   * 2 points: UI (e.g., Streamlit), web application (e.g., Django), or an API (e.g., built with FastAPI) 
* Ingestion pipeline
   * 2 points: Automated ingestion with a Python script or a special tool (e.g., Mage, dlt, Airflow, Prefect)
* Monitoring
   * 2 points: User feedback is collected and there's a dashboard with at least 5 charts
* Containerization
    * 2 points: Everything is in docker-compose
* Reproducibility
    * 2 points: Instructions are clear, the dataset is accessible, it's easy to run the code, and it works. The versions for all dependencies are specified.
* Best practices
    * 1 point: Hybrid search: combining both text and vector search (at least evaluating it)
    * 1 point: Document re-ranking
