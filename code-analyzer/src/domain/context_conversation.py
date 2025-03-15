from typing import List
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from ..utils import Extractor

from ..adapters.dtos import DocumentDTO
from . import RAG

class ContextConversation:

    @staticmethod
    def retriever(documents: List[DocumentDTO], embeddings: Embeddings) -> List[Document]:
        """
                Recupera documentos relevantes com base nos embeddings fornecidos.

                Args:
                    documents (List[DocumentDTO]): Uma lista de objetos DocumentDTO que contêm o conteúdo e os metadados dos documentos.
                    embeddings (Embeddings): Embeddings utilizados para a recuperação de documentos.

                Returns:
                    List[Document]: Uma lista de objetos Document contendo o texto extraído e os metadados.
        """
        buffer = []

        for document in documents:
            document_bytes_IO = Extractor.stream(document.content.parts)
            text = Extractor.extract_text(document_bytes_IO, document.content.content_type)
            metadata = document.metadata if document.metadata else {}
            document = Document(text, metadata=metadata)

            buffer.append(document)

        return RAG.retriever(buffer, embeddings)
