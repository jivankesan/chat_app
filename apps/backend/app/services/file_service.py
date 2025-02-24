# app/services/file_service.py

import numpy as np
from .text_extractor import PDFTextExtractor, DOCXTextExtractor, TXTTextExtractor
from .text_processor import TextProcessor
from .embeddings_manager import EmbeddingsManager

pdf_extractor = PDFTextExtractor()
docx_extractor = DOCXTextExtractor()
txt_extractor = TXTTextExtractor()

class FileService:
    def __init__(self, openai_client, config, embeddings_manager: EmbeddingsManager):
        self.openai_client = openai_client
        self.embeddings_manager = embeddings_manager
        self.text_processor = TextProcessor(config)

    def process_file_for_user(self, user_id: str, file_bytes: bytes, file_name: str):
        ext = file_name.split(".")[-1].lower()

        if ext == "pdf":
            text = pdf_extractor.extract_text(file_bytes)
        elif ext == "docx":
            text = docx_extractor.extract_text(file_bytes)
        else:
            text = txt_extractor.extract_text(file_bytes)

        # Create chunks
        chunks = self.text_processor.create_chunks(text)

        # Embed each chunk
        chunk_embeddings = []
        for c in chunks:
            emb = self.openai_client.create_embedding(c)
            chunk_embeddings.append(emb)
        chunk_embeddings = np.array(chunk_embeddings)

        # Add to the user’s FAISS index
        self.embeddings_manager.add_embeddings_for_user(user_id, chunk_embeddings, chunks)