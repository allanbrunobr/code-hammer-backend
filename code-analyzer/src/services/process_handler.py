import asyncio
import json
import logging
import requests
import traceback
import time
from typing import Optional

from pydantic import ValidationError
from ..adapters.dtos import UserPreferDTO
from .conversation import ConversationService
from .comment_poster import CommentPosterFactory
from .request_processor import RequestProcessor
from ..domain import LLMGateway, ModelEmbeddings
from .repository_manager import RepositoryManager
from .code_analyzer import CodeAnalyzer
from ..adapters.http_client import ConfigManagerClient

class ProcessHandler(RequestProcessor):
    logger = logging.getLogger(__name__)

    @staticmethod
    def process_message(message):
        """
        Processa uma mensagem recebida do Pub/Sub.
        
        Args:
            message: Mensagem recebida do Pub/Sub
        """
        start_time = time.time()
        ProcessHandler.logger.info(f"[CODE-ANALYZER] Recebendo mensagem do Pub/Sub: {message.message_id}")
        
        try:
            result = ProcessHandler.process_request(message.data)
            message.ack()
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Processamento concluído com sucesso em {time.time() - start_time:.2f} segundos")
        except Exception as e:
            ProcessHandler.logger.error(f"[CODE-ANALYZER] Erro ao processar mensagem: {str(e)}")
            ProcessHandler.logger.error(traceback.format_exc())
            # Ainda fazemos ack para não ficar reprocessando mensagens com erro
            message.ack()
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Mensagem marcada como processada (ack) apesar do erro")

    @staticmethod
    def process_request(message_data: bytes):
        """
        Processa os dados da mensagem para análise de código.
        
        Args:
            message_data: Dados da mensagem em bytes
        """
        repo_path = None
        try:
            # Decodificar a mensagem
            message_str = message_data.decode('utf-8')
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Mensagem recebida para processamento - Tamanho: {len(message_str)} bytes")
            
            # Converter para JSON
            user_json = json.loads(message_str)
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Dados do repositório recebidos: {json.dumps(user_json.get('repository', {}), indent=2)}")
            
            # Log do PR number antes da validação
            raw_pr = user_json.get('repository', {}).get('pull_request_number')
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Pull Request Number no JSON bruto: {raw_pr} (tipo: {type(raw_pr)})")
            
            # Verificações básicas
            if 'token' not in user_json or not user_json['token']:
                ProcessHandler.logger.error("[CODE-ANALYZER] Token não encontrado na mensagem")
                raise ValueError("Token de repositório é obrigatório")
                
            if 'repository' not in user_json:
                ProcessHandler.logger.error("[CODE-ANALYZER] Informações do repositório não encontradas na mensagem")
                raise ValueError("Informações do repositório são obrigatórias")
                
            # Validar dados usando o DTO
            user_prefer = UserPreferDTO(**user_json)
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Mensagem validada - Usuário: {user_prefer.email}, Repositório: {user_prefer.repository.type}")
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Owner/Repo: {user_prefer.repository.owner}/{user_prefer.repository.repo}")
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Token de acesso: {user_prefer.token[:5]}...") if user_prefer.token else ProcessHandler.logger.info("[CODE-ANALYZER] Sem token de acesso")
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Código fornecido: {'Vazio (analisando repositório inteiro)' if not user_prefer.code else f'{len(user_prefer.code)} caracteres'}")
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Idioma para análise: {user_prefer.language}")
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Pull Request Number após validação: {user_prefer.repository.pull_request_number} (tipo: {type(user_prefer.repository.pull_request_number)})")

            # Analisar o código
            analysis_result = None
            if not user_prefer.code:
                if user_prefer.repository.pull_request_number:
                    ProcessHandler.logger.info(f"[CODE-ANALYZER] Preparando para análise do PR #{user_prefer.repository.pull_request_number}")
                    repo_path = RepositoryManager.clone_and_analyze_repository(user_prefer, analyze_pr_only=True)
                    if repo_path:
                        ProcessHandler.logger.info(f"[CODE-ANALYZER] Repositório clonado em: {repo_path}")
                        analysis_result = CodeAnalyzer.analyze_pr(repo_path, user_prefer)
                    else:
                        raise ValueError("Falha ao clonar repositório")
                elif getattr(user_prefer, 'analyze_full_project', False):
                    ProcessHandler.logger.info("[CODE-ANALYZER] Flag analyze_full_project ativada - analisando todo o projeto")
                    repo_path = RepositoryManager.clone_and_analyze_repository(user_prefer)
                    if repo_path:
                        ProcessHandler.logger.info(f"[CODE-ANALYZER] Repositório clonado em: {repo_path}")
                        analysis_result = CodeAnalyzer.analyze_repository(repo_path, user_prefer)
                    else:
                        raise ValueError("Falha ao clonar repositório")
                else:
                    ProcessHandler.logger.info("[CODE-ANALYZER] Código vazio e sem PR - analisando todo o projeto")
                    repo_path = RepositoryManager.clone_and_analyze_repository(user_prefer)
                    if repo_path:
                        ProcessHandler.logger.info(f"[CODE-ANALYZER] Repositório clonado em: {repo_path}")
                        analysis_result = CodeAnalyzer.analyze_repository(repo_path, user_prefer)
                    else:
                        raise ValueError("Falha ao clonar repositório")
            else:
                ProcessHandler.logger.info("[CODE-ANALYZER] Analisando trecho de código específico")
                analysis_result = CodeAnalyzer.analyze_code(user_prefer.code, user_prefer)

            if not analysis_result:
                ProcessHandler.logger.error("[CODE-ANALYZER] Nenhum resultado de análise gerado")
                raise ValueError("Falha na análise do código")

            # Postar comentário se necessário
            ProcessHandler._post_analysis_comment(user_prefer, analysis_result)
            
            # Atualizar as métricas de quota de arquivos
            ProcessHandler._update_file_quota(user_prefer)

        except Exception as e:
            ProcessHandler.logger.error(f"[CODE-ANALYZER] Erro durante o processamento: {str(e)}")
            raise
        finally:
            # Limpar diretório temporário se existir
            if repo_path:
                RepositoryManager.cleanup_repository(repo_path)

    @staticmethod
    def _post_analysis_comment(user_prefer: UserPreferDTO, analysis_result: str):
        """
        Posta o resultado da análise como comentário no repositório.
        
        Args:
            user_prefer: Preferências do usuário
            analysis_result: Resultado da análise
        """
        try:
            # Verificar token
            if not user_prefer.token:
                ProcessHandler.logger.error("[CODE-ANALYZER] Token é obrigatório para postar comentários")
                raise ValueError("Token é obrigatório para postar comentários")

            # Log com informações sobre o token e repositório
            token_preview = user_prefer.token[:4] + "..." + user_prefer.token[-4:] if len(user_prefer.token) > 8 else "***"
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Token validado - Preview: {token_preview}")
            
            repo_info = f"Tipo: {user_prefer.repository.type}"
            if user_prefer.repository.owner:
                repo_info += f", Owner: {user_prefer.repository.owner}"
            if user_prefer.repository.repo:
                repo_info += f", Repo: {user_prefer.repository.repo}"
                
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Detalhes do repositório - {repo_info}")

            # Garantir que pull_request_number seja definido, mesmo que seja None
            if not hasattr(user_prefer.repository, 'pull_request_number') or user_prefer.repository.pull_request_number is None:
                ProcessHandler.logger.warning("[CODE-ANALYZER] Número do Pull Request não fornecido - será usado fallback")
                user_prefer.repository.pull_request_number = None

            # Criar o poster de comentários apropriado
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Criando poster de comentários para {user_prefer.repository.type}")
            comment_post = CommentPosterFactory.create_comment_poster(user_prefer)
            
            # Postar o comentário
            ProcessHandler.logger.info("[CODE-ANALYZER] Preparando para postar comentário no repositório")
            comment_post.post_comment(user_prefer, analysis_result)
            ProcessHandler.logger.info("[CODE-ANALYZER] Comentário postado com sucesso")

        except Exception as e:
            ProcessHandler.logger.error(f"[CODE-ANALYZER] Erro ao postar comentário: {str(e)}")
            raise
    
    @staticmethod
    def _update_file_quota(user_prefer: UserPreferDTO):
        """
        Atualiza as métricas de quota de arquivos do usuário após a análise.
        
        Args:
            user_prefer: Preferências do usuário com informações da análise
        """
        try:
            # Obter o número de arquivos no PR
            # Para fins de demonstração, estamos usando um valor fixo de 1 arquivo
            # Em uma implementação real, você deve contar o número de arquivos afetados pelo PR
            pr_file_count = 1
            
            # Se houver um PR associado à análise, contar os arquivos corretamente
            if hasattr(user_prefer.repository, 'pull_request_number') and user_prefer.repository.pull_request_number:
                # Aqui você pode implementar a lógica para contar os arquivos reais no PR
                # Por simplicidade, estamos usando valores fixos para demonstração
                if user_prefer.repository.type == 'Github':
                    # Exemplo: contar arquivos em um PR do GitHub
                    pr_file_count = 5  # Valor de exemplo
                elif user_prefer.repository.type == 'Gitlab':
                    # Exemplo: contar arquivos em um PR do GitLab
                    pr_file_count = 3  # Valor de exemplo
                elif user_prefer.repository.type == 'Azure':
                    # Exemplo: contar arquivos em um PR do Azure DevOps
                    pr_file_count = 4  # Valor de exemplo
                elif user_prefer.repository.type == 'Bitbucket':
                    # Exemplo: contar arquivos em um PR do Bitbucket
                    pr_file_count = 2  # Valor de exemplo
            
            # Extrair o e-mail do usuário para identificação
            # Em uma implementação real, você deve usar o ID do usuário
            user_email = user_prefer.email
            
            # Log para debug
            ProcessHandler.logger.info(f"[CODE-ANALYZER] Atualizando quota de arquivos para {user_email} com {pr_file_count} arquivos")
            
            # Atualizar a quota de arquivos no config-manager
            # Em uma implementação real, você deve usar o ID do usuário em vez do e-mail
            # Por simplicidade, estamos usando o e-mail como ID
            result = ConfigManagerClient.update_file_quota(user_email, pr_file_count)
            
            if result:
                ProcessHandler.logger.info(f"[CODE-ANALYZER] Quota de arquivos atualizada com sucesso. Arquivos avaliados: {result.get('evaluated_files')}, Arquivos disponíveis: {result.get('available_files')}")
            else:
                ProcessHandler.logger.warning(f"[CODE-ANALYZER] Falha ao atualizar quota de arquivos para {user_email}")
            
        except Exception as e:
            # Registrar o erro, mas não interromper o fluxo principal
            ProcessHandler.logger.error(f"[CODE-ANALYZER] Erro ao atualizar quota de arquivos: {str(e)}")
            # Não lançamos a exceção para não interromper o fluxo principal da aplicação
