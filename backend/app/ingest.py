import os
import json
import random
from dotenv import load_dotenv
from tqdm.auto import tqdm
from openai import OpenAI


load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")
INDEX_NAME = os.getenv("INDEX_NAME", "reviews-steam")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Define the prompt template for generating questions
prompt_template = """
You are a PC video game enthusiast who enjoys playing games on their release day.
You are aware that it is now common for developers to release unfinished or unoptimized products.
You understand that developers often fail to deliver on the promises made about a game prior to its release.
You prefer games that function well upon launch and are delivered with proper quality—titles that are not released prematurely.
Also, a user does not want to use any external applications for logging or sharing data. They want only to use Steam as a means of buying and playing video games.

Formulate 5 questions this user would ask based on the provided inputed review from Steam store.
Create only questions that are related to this exercise and type of user.
The record should contain the answer to the questions, and the questions should be complete and not too short. Use as few words as possible from the record.
That will be the answer field of our output JSON file.

After that, assign a single-word label to each question and store it as a label.
That will be the section field of our output JSON file.
The values for section can cover any issue a video gamer might be interested in: audio, video, hardware, plot, characters, game mechanics, multiplayer opponents' toxicity, game-breaking bugs, enemy variety, location variety, violence level, DEI (Diversity, Equity, Inclusion) presence, whether the game is complete, whether the game is functional, whether it is worth the price, etc. Be creative here.
Also in output JSON file, assign to each question-answer a review which was used for text generation.

The input record:

appid: {appid}
timestamp_query: {timestamp_query}
title: {title}
recommendationid: {recommendationid}
language: {language}
review: {review}
voted_up: {voted_up}
votes_up: {votes_up}
timestamp_created: {timestamp_created}
timestamp_updated: {timestamp_updated}

Provide the output in parsable JSON without using code blocks:

{{"review": ["review1"], "question": ["question1", "question2", ..., "question5"], "answer": ["answer1", "answer2", ..., "answer5"], "section": ["section1", "section2", ..., "section5"]}}
""".strip()

def load_reviews(data_dir):
    """Load reviews from JSON files in the specified directory."""
    reviews = []
    objects_in_directory = os.listdir(data_dir)
    print(f"Loading reviews from directory: {data_dir}...")
    print(f"Found {len(objects_in_directory)} objects in the directory.")

    for obj in objects_in_directory:
        if obj.endswith('.json'):
            file_path = os.path.join(data_dir, obj)
            print(f"Loading file: {file_path}...")
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                file_reviews = json.load(jsonfile)
                if isinstance(file_reviews, list):
                    reviews.extend(file_reviews)
                else:
                    reviews.append(file_reviews)
            print(f"Loaded {len(file_reviews)} reviews from {file_path}.")

    # Shuffle the reviews to randomize their order
    random.shuffle(reviews)
    print(f"Total reviews loaded and shuffled: {len(reviews)}")
    return reviews

def generate_questions(doc):
    """Generate questions and answers from a review document."""
    prompt = prompt_template.format(**doc)
    print(f"Generating questions for appid {doc['appid']}...")

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{"role": "user", "content": prompt}]
    )

    questions_data = json.loads(response.choices[0].message.content)
    print(f"Generated questions for appid {doc['appid']}: {questions_data['question']}")
    return questions_data

def save_results(final_results, output_file_path):
    """Save final results to a JSON file."""
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(final_results, output_file, ensure_ascii=False, indent=4)
    print(f"Processing complete. Final results saved to {output_file_path}.")

def process_documents(reviews):
    """Process reviews to generate questions and structure final results."""
    final_results = []
    unique_id_counter = 0
    print(f"Processing {len(reviews)} reviews...")

    for doc in tqdm(reviews):
        doc_id = doc['appid']
        print(f"Processing document with appid: {doc_id}...")

        try:
            # Generate questions, answers, and sections
            questions_data = generate_questions(doc)

            questions = questions_data['question']
            answers = questions_data['answer']
            sections = questions_data['section']

            for i in range(len(questions)):
                final_results.append({
                    "document_id": unique_id_counter,
                    "appid": doc_id,
                    "review": doc,
                    "question": questions[i],
                    "answer": answers[i],
                    "section": sections[i]
                })
                print(f"Added question {i+1} for appid {doc_id} to results.")
                unique_id_counter += 1

        except json.JSONDecodeError as e:
            print(f"Error processing document with appid {doc_id}: JSONDecodeError - {e}")
        except Exception as e:
            print(f"Error processing document with appid {doc_id}: {e}")

    print(f"Finished processing documents. Total processed: {len(final_results)}.")
    return final_results

def ingest_documents(directory_path):
    """Ingest documents from the specified directory path."""
    reviews = load_reviews(directory_path)
    print(f"Total documents ingested: {len(reviews)}")
    
    processed_documents = process_documents(reviews)
    print(f"Total documents ingested and processed: {len(processed_documents)}")
    
    # Save final results to the specified output path
    output_file_path = os.path.abspath('../llm-zoomcamp-capstone-01/data/ground_truth_retrieval.json')
    save_results(processed_documents, output_file_path)
    
    return processed_documents
