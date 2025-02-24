# app/services/text_extractor.py

import io
import docx
import pdfplumber

class BaseTextExtractor:
    def extract_text(self, file_bytes: bytes) -> str:
        raise NotImplementedError()

class PDFTextExtractor(BaseTextExtractor):
    def extract_text(self, file_bytes: bytes) -> str:
        main_text = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                bbox = (0, 50, page.width, page.height - 50)
                cropped_page = page.within_bbox(bbox)
                text = cropped_page.extract_text()
                if text:
                    main_text.append(text.strip())
        return "\n".join(main_text)

class DOCXTextExtractor(BaseTextExtractor):
    def extract_text(self, file_bytes: bytes) -> str:
        text = []
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text.append(para.text)
        return "\n".join(text)

class TXTTextExtractor(BaseTextExtractor):
    def extract_text(self, file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8")