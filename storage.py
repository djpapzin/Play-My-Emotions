import os
from typing import List, TypedDict
from uuid import uuid4
import redis

# Define the structure of user input data
class UserInput(TypedDict):
    text: str
    emotions: str
    songs: List[str]

# Class for Redis storage operations
class RedisStorage:
    def __init__(self, host: str, password: str):
        # Initialize Redis client
        self._client = redis.Redis(host=host, port="35043", password=password, ssl=True)

    # Function to store user input data in Redis
    def store(self, data: UserInput) -> bool:
        uid = uuid4()
        response = self._client.json().set(f"data:{uid}", "$", data)
        return response