import base64
import io
import fitz
from docx import Document
from typing import IO

class Extractor:

    @staticmethod
    def stream(content: str) -> IO[bytes]:
        data = base64.b64decode(content)
        stream = io.BytesIO(data)

        return stream

    @staticmethod
    def extract_text_from_pdf(stream: str | IO[bytes]) -> str:
        document = fitz.open(stream=stream, filetype="pdf")
        text = ""

        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()

        return text

    @staticmethod
    def extract_text_from_docx(stream: str | IO[bytes]) -> str:
        document = Document(stream)
        text = ""

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

        return text

    @staticmethod
    def extract_text(content:  str | IO[bytes], extension: str) -> str:
        extraction_methods = {
            'pdf': Extractor.extract_text_from_pdf,
            'docx': Extractor.extract_text_from_docx
        }
        name = extension.lower()

        if name in extraction_methods:
            try:
                method = extraction_methods[name]

                return method(Extractor.stream(content))
            except KeyError:
                raise ValueError("Unsupported file extension")

        return content
