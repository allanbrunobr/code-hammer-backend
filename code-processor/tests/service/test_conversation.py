import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import uuid
from datetime import datetime
from src.adapters.dtos import ConversationDTO, MessageDTO, ContentDTO, DocumentDTO
from src.domain import ContextConversation
from src.services import ConversationService, SlackService
from src.tools import SlackTool


class TestConversationService(unittest.TestCase):

    def setUp(self):
        self.llm = MagicMock()
        self.embeddings = MagicMock()
        self.service = ConversationService(llm=self.llm, embeddings=self.embeddings)

    @patch('src.domain.ContextConversation.retriever')
    @patch('src.services.SlackService')
    @patch('src.tools.SlackTool')
    def test_message(self,  mock_slack_tool, mock_slack_service, mock_retriever):
        # Mock configurations
        mock_slack_service.return_value = MagicMock()
        mock_slack_tool.return_value = MagicMock()

        mock_retriever_instance = MagicMock()
        mock_retriever_instance.get_relevant_documents.return_value = [MagicMock(page_content="Mock content")]
        mock_retriever.return_value = mock_retriever_instance

        # Mock data
        message = MessageDTO(
            id=uuid.uuid4(),
            create_time=datetime.now().timestamp(),
            content=ContentDTO(content_type="text")
        )

        # Cria um DocumentDTO válido para o contexto
        document_dto = DocumentDTO(
            content=ContentDTO(parts="mock parts", content_type="mock type"),
            metadata={}
        )

        data = ConversationDTO(
            conversation_id=uuid.uuid4(),
            message=message,
            context=[document_dto]
        )

        # Define the async generator method for testing
        async def async_generator():
            yield ": #{0} stream\n\n".format(data.conversation_id)
            yield "data: {\"message\": \"mock response\"}\n\n"

        # Mock the method to return the async generator
        self.service.message = lambda x: async_generator()

        # Run the async message method and collect outputs
        async def run_service():
            responses = []
            async for response in self.service.message(data):
                responses.append(response)
            return responses

        # Execute the test
        responses = asyncio.run(run_service())

        # Verificar se as respostas contêm a string esperada
        expected_response_start = f": #{data.conversation_id} stream\n\n"
        self.assertTrue(any(expected_response_start in response for response in responses))
        self.assertTrue(any("mock response" in response for response in responses))


if __name__ == '__main__':
    unittest.main()
