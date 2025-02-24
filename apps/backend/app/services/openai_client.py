# app/services/openai_client.py

from openai import AzureOpenAI

class OpenAIClient:
    """Handles direct calls to Azure/OpenAI endpoints."""

    def __init__(self, config):
        self.client = AzureOpenAI(
            azure_endpoint=config.MODEL_ENDPOINT,
            api_key=config.MODEL_API_KEY,
            api_version=config.API_VERSION
        )
        self.chat_model = config.MODEL_GENERATE
        self.embedding_model = config.MODEL_EMBED

    def create_embedding(self, text: str):
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding

    def generate_chat_completion(self, system_prompt: str, user_message: str):
        """Non-streaming version (for reference)."""
        completion = self.client.chat.completions.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=1000,
            temperature=0.7,
            top_p=0.95,
            stream=False
        )
        return completion.choices[0].message.content.strip()

    def stream_chat_completion(self, system_prompt: str, user_message: str):
        response = self.client.chat.completions.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=1000,
            temperature=0.7,
            top_p=0.95,
            stream=True
        )
        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and "content" in delta:
                yield delta["content"]