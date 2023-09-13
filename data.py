# Import necessary libraries and modules
from dotenv import load_dotenv
import json
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import DeepLake
from names import DATASET_ID, MODEL_ID

# Load environment variables
load_dotenv()

# Function to create a DeepLake database from a given dataset path and JSON file
def create_db(dataset_path: str, json_filepath: str) -> DeepLake:
    # Load data from the JSON file
    with open(json_filepath, "r") as f:
        data = json.load(f)

    # Extract texts and metadata from the data
    texts = []
    metadatas = []
    for movie, lyrics in data.items():
        for lyric in lyrics:
            texts.append(lyric["text"])
            metadatas.append(
                {
                    "movie": movie,
                    "name": lyric["name"],
                    "embed_url": lyric["embed_url"],
                }
            )

    # Initialize embeddings using OpenAI
    embeddings = OpenAIEmbeddings(model=MODEL_ID)

    # Create a DeepLake database from the texts and metadata
    db = DeepLake.from_texts(
        texts, embeddings, metadatas=metadatas, dataset_path=dataset_path
    )

    return db

# Function to load an existing DeepLake database
def load_db(dataset_path: str, *args, **kwargs) -> DeepLake:
    db = DeepLake(dataset_path, *args, **kwargs)
    return db

# If the script is executed directly, create a DeepLake database using the specified dataset path and JSON file
if __name__ == "__main__":
    dataset_path = f"hub://{os.environ['ACTIVELOOP_ORG_ID']}/{DATASET_ID}"
    create_db(dataset_path, "data/emotions_with_spotify_url.json")
