from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from ..utils import Environment
import logging

logger = logging.getLogger(__name__)

class LLMGateway(ChatVertexAI):

    def __init__(self):
        model_name = Environment.get("GOOGLE_AI_MODEL_NAME")
        project = Environment.get("GOOGLE_PROJECT")
        location = Environment.get("GOOGLE_LOCATION")

        super().__init__(model_name=model_name, project=project, location=location)
    
    @staticmethod
    def analyze_code(code: str, prompt: str = None, language: str = None) -> str:
        """
        Analisa o código usando o modelo de linguagem.
        
        Args:
            code: Código a ser analisado
            prompt: Prompt personalizado para análise (opcional)
            language: Linguagem de programação do código (opcional)
            
        Returns:
            str: Resultado da análise
        """
        try:
            # Inicializar o modelo
            model_name = Environment.get("GOOGLE_AI_MODEL_NAME")
            project = Environment.get("GOOGLE_PROJECT")
            location = Environment.get("GOOGLE_LOCATION")
            
            model = ChatVertexAI(model_name=model_name, project=project, location=location)
            
            # Usar o prompt personalizado ou o prompt padrão
            if not prompt:
                # Prompt padrão
                base_prompt = '''
                Você é um expert em análise de código e líder técnico. Analise este código, comente sobre ele e refatore as partes do código que têm bugs, vulnerabilidades e code smells.
                Comente se o código segue os fundamentos dos princípios OWASP e SOLID.
                Use a primeira pessoa como um líder técnico.
                Seja direto, sem apresentação, e sucinto pois você está criando um comentário de PR.
                '''
            else:
                # Usar o prompt personalizado
                base_prompt = prompt
            
            # Adicionar informação sobre a linguagem, se fornecida
            language_info = f"\nO código está escrito em {language}." if language else ""
            
            final_prompt = f'''
            {base_prompt}
            {language_info}
            
            ```
            {code}
            ```
            '''
            
            logger.info(f"[LLM-GATEWAY] Enviando {len(code)} caracteres para análise")
            
            # Enviar a solicitação
            messages = [HumanMessage(content=final_prompt)]
            response = model.invoke(messages)
            
            if not response or not response.content:
                raise ValueError("O modelo não retornou uma resposta válida")
                
            return response.content
            
        except Exception as e:
            logger.error(f"[LLM-GATEWAY] Erro ao analisar código: {str(e)}")
            raise ValueError(f"Erro na análise do código: {str(e)}")