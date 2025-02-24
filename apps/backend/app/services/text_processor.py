# app/services/text_processor.py

from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import AzureOpenAIEmbeddings

class TextProcessor:
    """
    Handles splitting of text into chunks using the `SemanticChunker`,
    or a fallback approach as needed.
    """
    def __init__(self, config, threshold_type="percentile", threshold_amount=88.0):
        self.embeddings = AzureOpenAIEmbeddings(
            model="text-embedding-ada-002",
            api_key=config.MODEL_API_KEY,
            api_version=config.API_VERSION
        )
        self.text_splitter = SemanticChunker(
            self.embeddings,
            breakpoint_threshold_type=threshold_type,
            breakpoint_threshold_amount=threshold_amount
        )

    def create_chunks(self, text: str, threshold: int = 55):
        docs = self.text_splitter.create_documents([text])
        combined_docs = []

        for doc in docs:
            current_content = doc.page_content.strip()
            if not combined_docs:
                combined_docs.append(current_content)
            else:
                if len(current_content) < threshold:
                    combined_docs[-1] += " " + current_content
                else:
                    combined_docs.append(current_content)

        # Replace newlines with spaces
        stripped_docs = [doc.replace("\n", " ") for doc in combined_docs]
        return stripped_docs