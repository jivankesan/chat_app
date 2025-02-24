# app/config.py

import os

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# For Azure OpenAI:
MODEL_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-03-15-preview")
MODEL_EMBED = "text-embedding-ada-002"
MODEL_GENERATE = "gpt-3.5-turbo"
MODEL_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")