import os
import json
import time
from openai import OpenAI
from read import ReviewReader
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# Load environment variables
load_dotenv()

# Environment variables
ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")
INDEX_NAME = os.getenv("INDEX_NAME", "reviews-steam")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize the ReviewReader with the required model
model_name = 'multi-qa-MiniLM-L6-cos-v1'
model = SentenceTransformer(model_name)
reader = ReviewReader(model=model)


# Function to search for reviews
def search(query, model=model, num_results=5):
    # Uses the ReviewReader to perform the search using KNN and keyword matching
    question = query['question']
    title = query['title']

    field='question_answer_vector'
    v_q = model.encode(question)

    return reader.read_reviews_knn_and_keyword(field=field, query=query, title=title, vector=v_q, num_results=num_results)


prompt_template = """
You're a a video game reviewer. Answer the QUESTION based on the CONTEXT from our reviews database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()


entry_template = """
review.title: {review.title}
review.review: {review.review}
answer: {answer}
section: {section}
""".strip()


# Function to build the prompt based on search results
def build_prompt(query, search_results):
    context = ""

    for doc in search_results:
        context = context + entry_template.format(**doc) + "\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

# Function to generate the LLM response from OpenAI
def llm(prompt, model="gpt-4o-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    answer = response.choices[0].message.content
    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }
    return answer, token_stats


# Templates
evaluation_prompt_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  "relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()

# Function to evaluate the relevance of the LLM-generated answer
def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt, model="gpt-4o-mini")
    
    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {
            "Relevance": "UNKNOWN",
            "Explanation": "Failed to parse evaluation"
        }
    
    return result, tokens

# Function to calculate the OpenAI cost based on token usage
def calculate_openai_cost(model, tokens):
    openai_cost = 0

    if model == "gpt-4o-mini":
        openai_cost = (
            tokens["prompt_tokens"] * 0.00015 + tokens["completion_tokens"] * 0.0006
        ) / 1000
    else:
        print("Model not recognized. OpenAI cost calculation failed.")

    return openai_cost

# Main RAG function to handle the query and LLM interaction
def rag_answer(query, title, model="gpt-4o-mini"):
    start_time = time.time()

    query = {"question": query, "title": title}
    # Search for reviews related to the query
    search_results = search(query)
    
    # Build the prompt from the search results
    prompt = build_prompt(query, search_results)
    
    # Get LLM-generated answer
    answer, token_stats = llm(prompt, model=model)
    
    # Evaluate the relevance of the answer
    relevance, rel_token_stats = evaluate_relevance(query, answer)

    # Response time
    response_time = time.time() - start_time
    
    # Calculate costs
    openai_cost_rag = calculate_openai_cost(model, token_stats)
    openai_cost_eval = calculate_openai_cost(model, rel_token_stats)

    openai_cost = openai_cost_rag + openai_cost_eval

    # Create final answer data
    answer_data = {
        "answer": answer,
        "model_used": model,
        "response_time": response_time,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get(
            "Explanation", "Failed to parse evaluation"
        ),
        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],
        "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
        "eval_completion_tokens": rel_token_stats["completion_tokens"],
        "eval_total_tokens": rel_token_stats["total_tokens"],
        "openai_cost": openai_cost,
    }

    return answer_data
