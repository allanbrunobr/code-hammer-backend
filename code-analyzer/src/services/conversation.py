import logging
import time

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.messages import merge_content, HumanMessage

class ConversationService:
    logger = logging.getLogger(__name__)
    llm: BaseChatModel
    embeddings: Embeddings

    def __init__(self, llm: BaseChatModel, embeddings: Embeddings):
        self.llm = llm
        self.embeddings = embeddings
        self.logger.info("[CONVERSATION] Serviço de conversação inicializado")

    def format_prompt(self, code: str):
        self.logger.info(f"[CONVERSATION] Formatando prompt para análise de código de {len(code)} caracteres")
        prompt = '''
            You are an expert code analyst and technical leader. I will analyze this code, comment on it, and refactor the parts of the code that have bugs, vulnerabilities, and code smells.
            I will comment on whether the code follows the fundamentals of OWASP and SOLID principles.
            Use the first person as a technical leader.
            Be direct, without presentation, and succinct as you are creating a PR comment.
            ```
            ''' + str(code) + '''
            ```
            You should format in markdown translated to PT-BR
            '''
        self.logger.info(f"[CONVERSATION] Prompt formatado com {len(prompt)} caracteres")
        self.logger.info(f"[CONVERSATION] Prévia do prompt: {prompt[:100].replace(chr(10), ' ')}...")
        return prompt

    def send_message(self, code: str) -> str:
        try:
            self.logger.info(f"[CONVERSATION] Iniciando análise de código - Tamanho: {len(code)} caracteres")
            start_time = time.time()
            
            prompt = self.format_prompt(code)
            self.logger.info(f"[CONVERSATION] Prompt preparado - Enviando para LLM")
            
            messages = [HumanMessage(content=prompt)]
            model_start_time = time.time()
            response = self.llm(messages)
            model_end_time = time.time()
            self.logger.info(f"[CONVERSATION] LLM respondeu em {model_end_time - model_start_time:.2f} segundos")
            
            result = response.content
            self.logger.info(f"[CONVERSATION] Análise concluída em {time.time() - start_time:.2f} segundos - Resposta: {len(result)} caracteres")
            
            # Log de uma amostra da resposta
            response_preview = result[:100].replace(chr(10), ' ') + '...' if len(result) > 100 else result
            self.logger.info(f"[CONVERSATION] Prévia da resposta: {response_preview}")
            
            return result
        except Exception as e:
            self.logger.error(f"[CONVERSATION] Erro na análise de código: {str(e)}")
            raise
