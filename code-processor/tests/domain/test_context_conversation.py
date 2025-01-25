import unittest
from unittest.mock import MagicMock, patch
from typing import List, Any, Optional

from src.adapters.dtos import ContentDTO
# Importar a classe e outras dependências do módulo onde elas estão definidas
from src.domain.context_conversation import ContextConversation
from src.adapters.dtos.document import DocumentDTO
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class TestContextConversation(unittest.TestCase):

    @patch('utils.extractor.Extractor.extract_text')
    @patch('src.domain.context_conversation.RAG.retriever')
    def test_retriever(self, mock_retriever, mock_extract_text):
        # Configurar os mocks
        mock_extract_text.return_value = "This is the extracted text"
        mock_retriever.return_value = [Document(page_content="This is the extracted text", metadata={})]

        # Criar instâncias válidas de ContentDTO e DocumentDTO
        content_dto = ContentDTO(parts="mock parts", content_type="mock type")
        document_dto = DocumentDTO(
            content=content_dto,
            metadata={}
        )
        embeddings = MagicMock(spec=Embeddings)

        # Chamar a função a ser testada
        result = ContextConversation.retriever([document_dto], embeddings)

        # Verificações
        mock_extract_text.assert_called_once_with("mock parts", "mock type")
        mock_retriever.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].page_content, "This is the extracted text")
        self.assertEqual(result[0].metadata, {})


if __name__ == '__main__':
    unittest.main()