import os
import shutil
import tempfile
import logging
from git import Repo, GitCommandError
import git
from typing import Optional, Tuple
from ..adapters.dtos import UserPreferDTO

# Initialize logger at module level
logger = logging.getLogger(__name__)

class RepositoryManager:
    """Manages repository operations such as cloning and file access."""

    @staticmethod
    def _parse_github_url(url: str) -> Tuple[str, str]:
        """
        Extrai owner e repo de uma URL do GitHub.
        
        Args:
            url: URL do repositório GitHub
            
        Returns:
            Tuple[str, str]: (owner, repo)
        """
        try:
            # Remover .git se presente
            if url.endswith('.git'):
                url = url[:-4]
                
            # Remover protocolo e domínio
            url = url.replace('https://', '').replace('http://', '')
            
            # Remover github.com se presente
            if url.startswith('github.com/'):
                url = url[11:]  # Remove 'github.com/'
            
            # Separar as partes
            parts = url.split('/')
            
            # Validar formato
            if len(parts) < 2:
                raise ValueError(f"URL inválida do GitHub. Formato esperado: [github.com/]owner/repo")
                
            owner = parts[0]
            repo = parts[1]
            
            # Validar owner e repo
            if not owner or not repo:
                raise ValueError("Owner ou repo não podem estar vazios")
                
            return owner, repo
            
        except Exception as e:
            logger.error(f"[REPO-MANAGER] Erro ao analisar URL do GitHub: {str(e)}")
            raise ValueError(f"URL inválida do GitHub: {url}. Erro: {str(e)}")

    @staticmethod
    def clone_and_analyze_repository(user_prefer: UserPreferDTO, analyze_pr_only: bool = False) -> Optional[str]:
        """
        Clona o repositório remoto e prepara para análise.
        
        Args:
            user_prefer: DTO com as preferências do usuário e dados do repositório
            
        Returns:
            Optional[str]: Caminho do diretório temporário onde o repositório foi clonado
        """
        temp_dir = None
        try:
            # Criar diretório temporário para o clone
            temp_dir = tempfile.mkdtemp()
            logger.info(f"[REPO-MANAGER] Diretório temporário criado: {temp_dir}")
            
            # Construir a URL do repositório com o token
            if user_prefer.repository.type == 'Github':
                # Verificar se temos owner e repo
                if not user_prefer.repository.owner or not user_prefer.repository.repo:
                    if not user_prefer.repository.repository_url:
                        raise ValueError("URL do repositório não fornecida")
                    owner, repo = RepositoryManager._parse_github_url(user_prefer.repository.repository_url)
                    user_prefer.repository.owner = owner
                    user_prefer.repository.repo = repo
                    logger.info(f"[REPO-MANAGER] Owner/Repo extraídos da URL: {owner}/{repo}")
                
                # Construir URL com token
                repo_url = f"https://{user_prefer.token}@github.com/{user_prefer.repository.owner}/{user_prefer.repository.repo}.git"
                logger.info(f"[REPO-MANAGER] URL do repositório construída com token")
            else:
                # Implementar outros provedores conforme necessário
                raise ValueError(f"Provedor de repositório não suportado: {user_prefer.repository.type}")
            
            logger.info(f"[REPO-MANAGER] Clonando repositório: {user_prefer.repository.owner}/{user_prefer.repository.repo}")
            
            try:
                # Tentar clonar o repositório
                repo = Repo.clone_from(repo_url, temp_dir)
                logger.info("[REPO-MANAGER] Repositório clonado com sucesso")

                if analyze_pr_only and user_prefer.repository.pull_request_number:
                    # Se for análise de PR, obter apenas os arquivos modificados
                    modified_files = RepositoryManager._fetch_pr_files(repo, user_prefer)
                    logger.info(f"[REPO-MANAGER] PR #{user_prefer.repository.pull_request_number} - {len(modified_files) if modified_files else 0} arquivos modificados encontrados")
                    
                    # Armazenar a lista de arquivos modificados para uso posterior
                    user_prefer.modified_files = modified_files
                
                # Verificar se o clone foi bem sucedido
                if not os.path.exists(os.path.join(temp_dir, '.git')):
                    raise GitCommandError('git clone', 'Clone incompleto - diretório .git não encontrado')
                
                return temp_dir
                
            except GitCommandError as e:
                logger.error(f"[REPO-MANAGER] Erro ao clonar repositório: {str(e)}")
                if 'Authentication failed' in str(e):
                    raise ValueError("Falha na autenticação do GitHub. Verifique se o token é válido e tem as permissões necessárias.")
                raise
            
        except Exception as e:
            logger.error(f"[REPO-MANAGER] Erro ao clonar repositório: {str(e)}")
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise
    
    @staticmethod
    def _fetch_pr_files(repo: git.Repo, user_prefer: UserPreferDTO):
        """
        Obtém os arquivos modificados no PR.
        
        Args:
            repo: Repositório Git
            user_prefer: Preferências do usuário
            
        Returns:
            List[str]: Lista de arquivos modificados no PR
        """
        try:
            # Fetch PR
            pr_number = user_prefer.repository.pull_request_number
            logger.info(f"[REPO-MANAGER] Iniciando fetch do PR #{pr_number}")
            
            # Fetch e adicione todas as referências remotas
            for remote in repo.remotes:
                remote.fetch()
            
            # Obter o commit base (target branch) - geralmente é main ou master
            target_branch = 'main'
            try:
                # Tentar diferentes nomes comuns para a branch principal
                if 'origin/main' in repo.refs:
                    target_branch = 'main'
                elif 'origin/master' in repo.refs:
                    target_branch = 'master'
                    
                logger.info(f"[REPO-MANAGER] Branch alvo detectada: {target_branch}")
                repo.git.checkout(f"origin/{target_branch}")
            except Exception as e:
                logger.warning(f"[REPO-MANAGER] Erro ao fazer checkout da branch alvo: {str(e)}")
            
            # GitHub PR access strategy 1: Use diretamente a GitHub API para obter arquivos modificados
            # Este é o método mais confiável, mas requer integração direta com a API GitHub
            if user_prefer.repository.type == 'Github' and user_prefer.repository.owner and user_prefer.repository.repo:
                try:
                    import requests
                    
                    # Construir URL da API 
                    api_url = f"https://api.github.com/repos/{user_prefer.repository.owner}/{user_prefer.repository.repo}/pulls/{pr_number}/files"
                    headers = {
                        "Authorization": f"token {user_prefer.token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                    
                    logger.info(f"[REPO-MANAGER] Obtendo arquivos do PR via API GitHub: {api_url}")
                    response = requests.get(api_url, headers=headers)
                    
                    if response.status_code == 200:
                        files_data = response.json()
                        modified_files = [file_data['filename'] for file_data in files_data]
                        logger.info(f"[REPO-MANAGER] {len(modified_files)} arquivos modificados encontrados via API GitHub")
                        
                        # Armazenar os arquivos modificados no objeto user_prefer para uso posterior
                        user_prefer.modified_files = modified_files
                        
                        # Log detalhado dos arquivos encontrados
                        logger.info(f"[REPO-MANAGER] ===== ARQUIVOS MODIFICADOS NO PR #{pr_number} (via API GitHub) =====")
                        for i, file in enumerate(modified_files, 1):
                            logger.info(f"[REPO-MANAGER]   {i}. {file}")
                        
                        # Imprimir em formato JSON para facilitar cópia
                        import json
                        logger.info(f"[REPO-MANAGER] RESULTADO JSON: {json.dumps(modified_files, indent=2)}")
                        
                        # Tentar fazer checkout do PR para ter acesso às modificações
                        try:
                            # Try multiple reference formats
                            for ref_format in [
                                f"refs/pull/{pr_number}/head",
                                f"pull/{pr_number}/head",
                                f"pr_{pr_number}"
                            ]:
                                try:
                                    logger.info(f"[REPO-MANAGER] Tentando checkout para referência: {ref_format}")
                                    repo.git.checkout(ref_format)
                                    logger.info(f"[REPO-MANAGER] Checkout bem-sucedido para: {ref_format}")
                                    return modified_files
                                except Exception as e:
                                    logger.warning(f"[REPO-MANAGER] Não foi possível fazer checkout de {ref_format}: {str(e)}")
                            
                            # Se nenhum checkout funcionou, tente criar um branch local
                            try:
                                logger.info(f"[REPO-MANAGER] Criando branch local para o PR #{pr_number}")
                                repo.git.fetch('origin', f"pull/{pr_number}/head:pr_{pr_number}")
                                repo.git.checkout(f"pr_{pr_number}")
                                logger.info(f"[REPO-MANAGER] Checkout bem-sucedido para branch local pr_{pr_number}")
                                return modified_files
                            except Exception as e:
                                logger.warning(f"[REPO-MANAGER] Não foi possível criar branch local: {str(e)}")
                            
                            # Mesmo sem checkout bem-sucedido, retornamos os arquivos da API
                            logger.warning("[REPO-MANAGER] Não foi possível fazer checkout do PR, mas os arquivos foram obtidos via API")
                            return modified_files
                            
                        except Exception as e:
                            logger.warning(f"[REPO-MANAGER] Erro ao fazer checkout do PR após obter arquivos via API: {str(e)}")
                            # Ainda temos os arquivos da API, podemos prosseguir
                            return modified_files
                    else:
                        logger.error(f"[REPO-MANAGER] Erro ao obter arquivos via API GitHub. Status: {response.status_code}, Resposta: {response.text}")
                except Exception as e:
                    logger.error(f"[REPO-MANAGER] Erro ao usar API GitHub para obter arquivos do PR: {str(e)}")
            
            # GitHub PR access strategy 2: Fetch the PR and create a local branch
            if user_prefer.repository.type == 'Github':
                try:
                    # Fetch PR reference directly
                    logger.info(f"[REPO-MANAGER] Executando fetch específico para o PR #{pr_number}")
                    repo.git.fetch('origin', f'pull/{pr_number}/head:pr_{pr_number}')
                    
                    # Try to checkout the local branch we just created
                    logger.info(f"[REPO-MANAGER] Tentando checkout para branch local pr_{pr_number}")
                    repo.git.checkout(f"pr_{pr_number}")
                    logger.info(f"[REPO-MANAGER] Checkout do PR realizado com sucesso")
                    
                    # Get modified files using git diff
                    logger.info(f"[REPO-MANAGER] Obtendo arquivos modificados via git diff")
                    diff_output = repo.git.diff(f"origin/{target_branch}", "--name-only")
                    modified_files = [file.strip() for file in diff_output.split('\n') if file.strip()]
                    
                    logger.info(f"[REPO-MANAGER] {len(modified_files)} arquivos modificados encontrados via git diff")
                    
                    # Armazenar os arquivos modificados no objeto user_prefer para uso posterior
                    user_prefer.modified_files = modified_files
                    
                    # Log dos arquivos encontrados
                    for file in modified_files:
                        logger.info(f"[REPO-MANAGER] Arquivo modificado: {file}")
                        
                    return modified_files
                except Exception as e:
                    logger.warning(f"[REPO-MANAGER] Erro na estratégia 2 de acesso ao PR: {str(e)}")
            
            # Estratégia 3: Try fallback to using origin/main and create a worktree
            try:
                logger.warning("[REPO-MANAGER] Usando estratégia alternativa para o PR")
                
                # Fallback to using origin/main
                repo.git.checkout(f"origin/{target_branch}")
                logger.info(f"[REPO-MANAGER] Checkout para origin/{target_branch} realizado como fallback")
                
                # If we're here, we couldn't access the PR files directly
                # For now, return an empty list of files
                logger.warning("[REPO-MANAGER] Não foi possível obter arquivos do PR")
                return []
                
            except Exception as e:
                logger.error(f"[REPO-MANAGER] Erro na estratégia 3 (fallback): {str(e)}")
                return []
            
        except Exception as e:
            logger.error(f"[REPO-MANAGER] Erro ao obter arquivos do PR: {str(e)}")
            raise

    @staticmethod
    def cleanup_repository(repo_path: str):
        """
        Limpa o diretório temporário do repositório.
        
        Args:
            repo_path: Caminho do diretório temporário
        """
        try:
            if repo_path and os.path.exists(repo_path):
                shutil.rmtree(repo_path)
                logger.info(f"[REPO-MANAGER] Diretório temporário removido: {repo_path}")
        except Exception as e:
            logger.error(f"[REPO-MANAGER] Erro ao limpar diretório temporário: {str(e)}")
