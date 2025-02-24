# app/services/chat_service.py

import time
from sqlalchemy.orm import Session
# from app.models.chat_history import ChatHistory   # example if you had a ChatHistory table

class ChatService:
    def __init__(self, openai_client, config, embeddings_manager):
        self.openai_client = openai_client
        self.embeddings_manager = embeddings_manager
        self.system_prompt = "You are a helpful assistant that uses relevant documents as context."

    def handle_user_query(self, user_id: str, user_query: str, db: Session):
        """Non-streaming usage (kept for reference)."""
        query_embedding = self.openai_client.create_embedding(user_query)
        relevant_text = self.embeddings_manager.search_user_index(user_id, query_embedding, k=5)
        user_message = f"Relevant docs:\n{relevant_text}\n\nUser Query:\n{user_query}"

        model_response = self.openai_client.generate_chat_completion(
            system_prompt=self.system_prompt,
            user_message=user_message
        )

        time.sleep(1)
        # Example: store chat record
        # chat_record = ChatHistory(
        #     user_id=user_id,
        #     user_query=user_query,
        #     model_response=model_response
        # )
        # db.add(chat_record)
        # db.commit()
        # db.refresh(chat_record)

        return model_response

    async def handle_user_query_stream(self, user_id: str, user_query: str, db: Session):
        """
        Streaming usage: yields partial text.
        Store final text in DB after streaming completes.
        """
        query_embedding = self.openai_client.create_embedding(user_query)
        relevant_text = self.embeddings_manager.search_user_index(user_id, query_embedding, k=5)
        user_message = f"Relevant docs:\n{relevant_text}\n\nUser Query:\n{user_query}"

        full_response = ""
        for chunk in self.openai_client.stream_chat_completion(self.system_prompt, user_message):
            full_response += chunk
            yield chunk

        time.sleep(1)
        # store final result in DB if desired
        # chat_record = ChatHistory(...)
        # db.add(chat_record)
        # db.commit()