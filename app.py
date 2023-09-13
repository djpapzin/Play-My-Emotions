# Import necessary libraries and modules
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from data import load_db
from names import DATASET_ID, MODEL_ID
from storage import RedisStorage
from utils import weighted_random_sample
import os
import numpy as np

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Play My Emotions API", description="API for emotion-based song recommendation", version="1.0")

# Define request and response models
class EmotionInput(BaseModel):
    emotion_text: str

class SongRecommendation(BaseModel):
    emotions: str
    recommended_songs: list

# Check if storage is enabled
USE_STORAGE = os.environ.get("USE_STORAGE", "True").lower() in ("true", "t", "1")

# Initialize necessary components for the app
def init():
    embeddings = OpenAIEmbeddings(model=MODEL_ID)
    dataset_path = f"hub://{os.environ['ACTIVELOOP_ORG_ID']}/{DATASET_ID}"

    db = load_db(
        dataset_path,
        embedding_function=embeddings,
        token=os.environ["ACTIVELOOP_TOKEN"],
        read_only=True,
    )

    storage = RedisStorage(
        host=os.environ["UPSTASH_URL"], password=os.environ["UPSTASH_PASSWORD"]
    )
    prompt = PromptTemplate(
        input_variables=["user_input"],
        template=Path("prompts/bot.prompt").read_text(),
    )

    llm = ChatOpenAI(temperature=0.3)
    chain = LLMChain(llm=llm, prompt=prompt)

    return db, storage, chain

db, storage, chain = init()

# Define API endpoint for song recommendation
@app.post("/recommend", response_model=SongRecommendation)
async def recommend_song(emotion: EmotionInput):
    user_input = emotion.emotion_text
    if not user_input:
        raise HTTPException(status_code=400, detail="Emotion input is required")

    docs, emotions = get_song(user_input, k=20)  # Assuming max_number_of_songs is 20 for now
    recommended_songs = [doc.metadata["name"] for doc in docs]

    return {"emotions": emotions, "recommended_songs": recommended_songs}

# Helper function to get song based on user input
def get_song(user_input: str, k: int = 20):
    emotions = chain.run(user_input=user_input)
    matches = db.similarity_search_with_score(emotions, distance_metric="cos", k=k)
    docs, scores = zip(
        *normalize_scores_by_sum(filter_scores(matches, 0.8))  # Assuming filter_threshold is 0.8 for now
    )
    choosen_docs = weighted_random_sample(
        np.array(docs), np.array(scores), n=2  # Assuming number_of_displayed_songs is 2 for now
    ).tolist()
    return choosen_docs, emotions

# Helper function to filter scores
def filter_scores(matches, th: float = 0.8):
    return [(doc, score) for (doc, score) in matches if score > th]

# Helper function to normalize scores
def normalize_scores_by_sum(matches):
    scores = [score for _, score in matches]
    tot = sum(scores)
    return [(doc, (score / tot)) for doc, score in matches]

# Run the app using uvicorn when the script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
