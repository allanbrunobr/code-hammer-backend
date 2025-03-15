import os
import logging
import git
from typing import Optional, List
from ..adapters.dtos import UserPreferDTO
from ..domain import LLMGateway, ModelEmbeddings

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    @staticmethod
    def analyze_repository(repo_path: str, user_prefer: UserPreferDTO) -> Optional[str]:
        """
        Analisa todo o repositório clonado.
        
        Args:
            repo_path: Caminho do diretório onde o repositório foi clonado
            user_prefer: Preferências do usuário
            
        Returns:
            Optional[str]: Resultado da análise
        """
        try:
            logger.info(f"[CODE-ANALYZER] Iniciando análise do repositório em: {repo_path}")
            
            # Inicializar LLM e embeddings
            llm = LLMGateway()
            embeddings = ModelEmbeddings()
            
            # Coletar todos os arquivos relevantes
            all_code = ""
            for root, _, files in os.walk(repo_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                all_code += f"\n# File: {os.path.relpath(file_path, repo_path)}\n{content}\n"
                        except Exception as e:
                            logger.warning(f"[CODE-ANALYZER] Erro ao ler arquivo {file_path}: {str(e)}")
            
            if not all_code:
                logger.warning("[CODE-ANALYZER] Nenhum arquivo de código encontrado no repositório")
                return "Nenhum arquivo de código fonte encontrado para análise."
            
            # Analisar o código coletado
            logger.info(f"[CODE-ANALYZER] Analisando {len(all_code)} caracteres de código")
            analysis_result = llm.analyze_code(all_code)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"[CODE-ANALYZER] Erro ao analisar repositório: {str(e)}")
            raise

    @staticmethod
    def analyze_pr(repo_path: str, user_prefer: UserPreferDTO) -> str:
        """
        Analisa apenas os arquivos modificados no PR.
        
        Args:
            repo_path: Caminho do repositório
            user_prefer: Preferências do usuário
            
        Returns:
            str: Resultado da análise
        """
        try:
            logger.info(f"[CODE-ANALYZER] Iniciando análise do PR #{user_prefer.repository.pull_request_number}")
            
            # Obter lista de arquivos modificados no PR
            modified_files = CodeAnalyzer._get_pr_modified_files(repo_path, user_prefer)
            
            if not modified_files:
                logger.warning("[CODE-ANALYZER] Nenhum arquivo modificado encontrado no PR")
                return "Nenhuma modificação encontrada para análise.\n\nVerifique se o PR contém alterações e se o token de acesso tem permissões suficientes para acessar o repositório."
            
            # Filtrar apenas arquivos de código-fonte
            code_files = []
            for file_path in modified_files:
                # Verificar extensões de código-fonte comuns
                if any(file_path.endswith(ext) for ext in 
                      ('.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', 
                       '.rb', '.c', '.cpp', '.h', '.hpp', '.cs', '.php', 
                       '.swift', '.kt', '.rs', '.scala', '.sh', '.bash')):
                    code_files.append(file_path)
                else:
                    logger.info(f"[CODE-ANALYZER] Ignorando arquivo não-código: {file_path}")
            
            # Se não encontrarmos arquivos de código, usar todos os arquivos
            if not code_files:
                logger.warning("[CODE-ANALYZER] Nenhum arquivo de código encontrado, usando todos os arquivos modificados")
                code_files = modified_files
            
            # Limitar quantidade de arquivos para não estourar limites de tokens
            if len(code_files) > 20:
                logger.warning(f"[CODE-ANALYZER] Muitos arquivos ({len(code_files)}), limitando a 20")
                code_files = code_files[:20]
            
            # Concatenar conteúdo dos arquivos modificados
            all_code = ""
            processed_files = []
            
            for file_path in code_files:
                abs_path = os.path.join(repo_path, file_path)
                if not os.path.exists(abs_path):
                    logger.warning(f"[CODE-ANALYZER] Arquivo não encontrado: {file_path}")
                    continue
                    
                try:
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        # Ignorar arquivos vazios
                        if not file_content.strip():
                            logger.info(f"[CODE-ANALYZER] Arquivo vazio ignorado: {file_path}")
                            continue
                        # Adicionar o conteúdo com cabeçalho
                        all_code += f"\n\n# Arquivo: {file_path}\n{file_content}"
                        processed_files.append(file_path)
                except Exception as e:
                    logger.warning(f"[CODE-ANALYZER] Erro ao ler arquivo {file_path}: {str(e)}")
            
            if not all_code.strip():
                logger.warning("[CODE-ANALYZER] Nenhum conteúdo de código encontrado nos arquivos modificados")
                return "Não foi encontrado conteúdo de código válido nos arquivos modificados no PR."
            
            logger.info(f"[CODE-ANALYZER] Analisando {len(all_code)} caracteres de código de {len(processed_files)} arquivos")
            logger.info(f"[CODE-ANALYZER] Arquivos processados: {', '.join(processed_files)}")
            
            def format_prompt(file_path: str, code: str, user_prefer: UserPreferDTO) -> str:
                # Usar o prompt personalizado que já contém os tipos de análise
                base_prompt = user_prefer.prompt
                
                # Extrair os tipos de análise do prompt de forma mais precisa
                analysis_types = []
                logger.info("[CODE-ANALYZER] Extraindo tipos de análise do prompt")
                
                # Verificar se o prompt contém a frase "analyze this code for:"
                if "analyze this code for:" in base_prompt.lower():
                    # Extrair a parte após "analyze this code for:"
                    analysis_part = base_prompt.lower().split("analyze this code for:")[1]
                    # Extrair até o próximo ponto ou final da string
                    if "." in analysis_part:
                        analysis_part = analysis_part.split(".")[0]
                    
                    logger.info(f"[CODE-ANALYZER] Parte do prompt com tipos de análise: '{analysis_part}'")
                    
                    # Mapeamento de termos específicos para tipos de análise
                    analysis_mappings = {
                        "code quality": "code quality",
                        "quality": "code quality",
                        "security": "security issues",
                        "security issues": "security issues",
                        "performance": "performance optimizations",
                        "performance optimizations": "performance optimizations",
                        "bugs": "bugs and logical errors",
                        "logical errors": "bugs and logical errors",
                        "code smells": "code smells",
                        "vulnerabilities": "security vulnerabilities",
                        "owasp": "OWASP principles",
                        "owasp principles": "OWASP principles",
                        "solid": "SOLID principles",
                        "solid principles": "SOLID principles",
                        "componentization": "componentization",
                        "componentizacao": "componentization",
                        "componentização": "componentization",
                        "optimization": "optimization",
                        "otimizacao": "optimization",
                        "otimização": "optimization",
                        "big o": "algorithmic complexity",
                        "algorithmic complexity": "algorithmic complexity",
                        "duplication": "duplication",
                        "duplicidade": "duplication",
                        "duplicação": "duplication"
                    }
                    
                    # Verificar cada termo no mapeamento
                    for term, analysis_type in analysis_mappings.items():
                        if term in analysis_part:
                            analysis_types.append(analysis_type)
                            logger.info(f"[CODE-ANALYZER] Detectado tipo de análise: {analysis_type} (de '{term}')")
                else:
                    # Fallback: verificar termos comuns no prompt inteiro
                    logger.info("[CODE-ANALYZER] Não encontrou 'analyze this code for:', verificando termos comuns")
                    
                    # Mapeamento de termos comuns para tipos de análise
                    fallback_keywords = {
                        "quality": "code quality",
                        "qualidade": "code quality",
                        "security": "security issues",
                        "seguranca": "security issues",
                        "performance": "performance optimizations",
                        "desempenho": "performance optimizations",
                        "bugs": "bugs and logical errors",
                        "erros": "bugs and logical errors",
                        "code smell": "code smells",
                        "vulnerabilit": "security vulnerabilities",
                        "owasp": "OWASP principles",
                        "solid": "SOLID principles",
                        "componentizacao": "componentization",
                        "componentização": "componentization",
                        "otimizacao": "optimization",
                        "otimização": "optimization",
                        "big o": "algorithmic complexity",
                        "complexidade": "algorithmic complexity",
                        "duplicidade": "duplication",
                        "duplicação": "duplication"
                    }
                    
                    # Extrair tipos de análise do prompt completo
                    for keyword, analysis_type in fallback_keywords.items():
                        if keyword in base_prompt.lower():
                            analysis_types.append(analysis_type)
                            logger.info(f"[CODE-ANALYZER] Detectado tipo de análise (fallback): {analysis_type}")
                
                # Remover duplicatas
                analysis_types = list(set(analysis_types))
                
                # Log dos tipos de análise detectados
                logger.info(f"[CODE-ANALYZER] Tipos de análise detectados: {', '.join(analysis_types)}")
                
                # Criar um template dinâmico baseado nos tipos de análise
                template_sections = []
                
                # Mapeamento específico para os tipos de análise do sistema
                template_mapping = {
                    # Tipos específicos do sistema
                    "Princípios SOLID": "Princípios SOLID:\n  [Avalie se o código segue os princípios SOLID (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) e sugira melhorias.]",
                    "Código Limpo": "Código Limpo:\n  [Avalie a legibilidade, simplicidade e organização do código. Sugira melhorias para tornar o código mais limpo e fácil de manter.]",
                    "Code Smells": "Code Smells:\n  [Identifique code smells (indicadores de problemas potenciais no código) e sugira refatorações para melhorar a qualidade do código.]",
                    "Vulnerabilidades (OWASP)": "Vulnerabilidades (OWASP):\n  [Identifique vulnerabilidades de segurança relacionadas aos princípios do OWASP (Open Web Application Security Project) e sugira correções.]",
                    "Componentização": "Componentização:\n  [Avalie a estrutura de componentes do código, a separação de responsabilidades e a reutilização. Sugira melhorias na organização dos componentes.]",
                    "Otimização (BIG O)": "Otimização (BIG O):\n  [Analise a complexidade algorítmica (Big O) do código e sugira otimizações para melhorar a eficiência e o desempenho.]",
                    "Duplicação": "Duplicação:\n  [Identifique código duplicado ou repetitivo e sugira refatorações para melhorar a reutilização e manutenibilidade.]",
                    "Boas práticas da Linguagem": "Boas práticas da Linguagem:\n  [Avalie se o código segue as boas práticas e convenções da linguagem de programação utilizada. Sugira melhorias específicas da linguagem.]",
                    "Boas práticas do Framework": "Boas práticas do Framework:\n  [Avalie se o código segue as boas práticas e padrões recomendados do framework utilizado. Sugira melhorias específicas do framework.]",
                    
                    # Mapeamentos alternativos para compatibilidade
                    "code quality": "Código Limpo:\n  [Avalie a legibilidade, simplicidade e organização do código. Sugira melhorias para tornar o código mais limpo e fácil de manter.]",
                    "security issues": "Vulnerabilidades (OWASP):\n  [Identifique vulnerabilidades de segurança relacionadas aos princípios do OWASP (Open Web Application Security Project) e sugira correções.]",
                    "performance optimizations": "Otimização (BIG O):\n  [Analise a complexidade algorítmica (Big O) do código e sugira otimizações para melhorar a eficiência e o desempenho.]",
                    "bugs and logical errors": "Code Smells:\n  [Identifique code smells (indicadores de problemas potenciais no código) e sugira refatorações para melhorar a qualidade do código.]",
                    "code smells": "Code Smells:\n  [Identifique code smells (indicadores de problemas potenciais no código) e sugira refatorações para melhorar a qualidade do código.]",
                    "security vulnerabilities": "Vulnerabilidades (OWASP):\n  [Identifique vulnerabilidades de segurança relacionadas aos princípios do OWASP (Open Web Application Security Project) e sugira correções.]",
                    "OWASP principles": "Vulnerabilidades (OWASP):\n  [Identifique vulnerabilidades de segurança relacionadas aos princípios do OWASP (Open Web Application Security Project) e sugira correções.]",
                    "SOLID principles": "Princípios SOLID:\n  [Avalie se o código segue os princípios SOLID (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) e sugira melhorias.]",
                    "componentization": "Componentização:\n  [Avalie a estrutura de componentes do código, a separação de responsabilidades e a reutilização. Sugira melhorias na organização dos componentes.]",
                    "optimization": "Otimização (BIG O):\n  [Analise a complexidade algorítmica (Big O) do código e sugira otimizações para melhorar a eficiência e o desempenho.]",
                    "algorithmic complexity": "Otimização (BIG O):\n  [Analise a complexidade algorítmica (Big O) do código e sugira otimizações para melhorar a eficiência e o desempenho.]",
                    "duplication": "Duplicação:\n  [Identifique código duplicado ou repetitivo e sugira refatorações para melhorar a reutilização e manutenibilidade.]",
                    "language best practices": "Boas práticas da Linguagem:\n  [Avalie se o código segue as boas práticas e convenções da linguagem de programação utilizada. Sugira melhorias específicas da linguagem.]",
                    "framework best practices": "Boas práticas do Framework:\n  [Avalie se o código segue as boas práticas e padrões recomendados do framework utilizado. Sugira melhorias específicas do framework.]"
                }
                
                # Para qualquer tipo de análise não mapeado, criar uma seção genérica
                for analysis_type in analysis_types:
                    if analysis_type in template_mapping:
                        template_sections.append(template_mapping[analysis_type])
                    else:
                        # Criar uma seção genérica para tipos não mapeados
                        # Capitalizar a primeira letra e substituir underscores por espaços
                        section_title = analysis_type.replace('_', ' ').title()
                        template_sections.append(f"{section_title}:\n  [Analise o código em relação a {analysis_type} e forneça sugestões de melhoria.]")
                
                # Sempre incluir considerações gerais
                template_sections.append("Considerações gerais:\n  [Faça recomendações gerais para melhorar o código, como modularização, legibilidade, uso de boas práticas, etc.]")
                
                # Atualizar a lista de tipos de análise para log
                logger.info(f"[CODE-ANALYZER] Tipos de análise que serão incluídos no template: {', '.join(analysis_types)}")
                
                # Criar o prompt com o template específico
                template_text = "\n\n".join(template_sections)
                prompt_template = f"""
Você é um expert em análise de código. Analise o seguinte código e forneça feedback seguindo exatamente o formato abaixo.

- Codigo: {file_path}
{code}

{base_prompt}

Formate sua resposta seguindo EXATAMENTE este template:

{template_text}
"""
                # Log do prompt completo
                logger.info(f"[CODE-ANALYZER] Prompt completo para análise:\n{'-'*50}\n{prompt_template}\n{'-'*50}")
                
                return prompt_template

            # Analisar o código usando o LLM
            try:
                analysis_result = ""
                
                # Adicionar resumo dos arquivos analisados no início do resultado
                file_summary = f"**Arquivos analisados ({len(processed_files)}):**\n"
                for i, file in enumerate(processed_files, 1):
                    file_summary += f"{i}. `{file}`\n"
                
                analysis_result += file_summary + "\n"

                # Processar cada arquivo individualmente para melhor formatação
                for file_path in processed_files:
                    # Extrair o conteúdo do arquivo do código concatenado
                    file_content = ""
                    try:
                        # Tentar extrair o conteúdo do arquivo do código concatenado
                        parts = all_code.split(f"\n\n# Arquivo: {file_path}\n")
                        if len(parts) > 1:
                            # Pegar o conteúdo após o cabeçalho do arquivo
                            file_content = parts[1].split("\n\n# Arquivo:")[0] if "\n\n# Arquivo:" in parts[1] else parts[1]
                        
                        # Se não conseguir extrair, ler o arquivo novamente
                        if not file_content:
                            abs_path = os.path.join(repo_path, file_path)
                            with open(abs_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                    except Exception as e:
                        logger.warning(f"[CODE-ANALYZER] Erro ao extrair conteúdo do arquivo {file_path}: {str(e)}")
                        continue
                    
                    # Criar o prompt formatado para este arquivo
                    prompt = format_prompt(file_path, file_content, user_prefer)
                    
                    # Analisar o arquivo
                    logger.info(f"[CODE-ANALYZER] Analisando arquivo: {file_path}")
                    file_analysis = LLMGateway.analyze_code(
                        code=file_content,
                        prompt=prompt,
                        language=user_prefer.language
                    )
                    
                    # Adicionar a análise ao resultado
                    analysis_result += f"\n## Arquivo: {file_path}\n\n{file_analysis}\n\n"
                    logger.info(f"[CODE-ANALYZER] Análise concluída para: {file_path}")
                
                return analysis_result
                
            except Exception as e:
                logger.error(f"[CODE-ANALYZER] Erro ao enviar código para análise: {str(e)}")
                fallback_message = (
                    f"Erro ao analisar o código do PR. Detalhes: {str(e)}\n\n"
                    f"Foram encontrados {len(processed_files)} arquivos modificados no PR:\n"
                )
                for file in processed_files:
                    fallback_message += f"- {file}\n"
                return fallback_message
            
        except Exception as e:
            logger.error(f"[CODE-ANALYZER] Erro ao analisar PR: {str(e)}")
            return f"Erro ao analisar o PR #{user_prefer.repository.pull_request_number}. Detalhes: {str(e)}"

    @staticmethod
    def _get_pr_modified_files(repo_path: str, user_prefer: UserPreferDTO) -> List[str]:
        """
        Obtém a lista de arquivos modificados no PR.
        
        Args:
            repo_path: Caminho do repositório
            user_prefer: Preferências do usuário
            
        Returns:
            List[str]: Lista de caminhos dos arquivos modificados
        """
        try:
            # Se já temos a lista de arquivos modificados de RepositoryManager, usá-la diretamente
            if hasattr(user_prefer, 'modified_files') and user_prefer.modified_files:
                logger.info(f"[CODE-ANALYZER] Usando lista de {len(user_prefer.modified_files)} arquivos modificados fornecida pelo RepositoryManager")
                # Filtrar apenas arquivos existentes
                valid_files = [
                    f for f in user_prefer.modified_files 
                    if os.path.exists(os.path.join(repo_path, f))
                ]
                logger.info(f"[CODE-ANALYZER] {len(valid_files)} arquivos existem no repositório local")
                
                # Log detalhado dos arquivos encontrados
                logger.info("[CODE-ANALYZER] ===== ARQUIVOS MODIFICADOS NO PR (via RepositoryManager) =====")
                for i, file in enumerate(valid_files, 1):
                    logger.info(f"[CODE-ANALYZER]   {i}. {file}")
                
                # Imprimir em formato JSON para facilitar cópia
                import json
                logger.info(f"[CODE-ANALYZER] RESULTADO JSON: {json.dumps(valid_files, indent=2)}")
                
                return valid_files
                
            # Caso não tenhamos a lista, tentar obtê-la através do git
            logger.info("[CODE-ANALYZER] Lista de arquivos não fornecida por RepositoryManager, tentando obtê-la via git")
            repo = git.Repo(repo_path)
            
            # Determinar a branch base do PR (geralmente main ou master)
            # Tentar usar a branch mais provável
            base_branch = 'main'
            for branch_name in ['main', 'master', 'develop']:
                try:
                    if f'origin/{branch_name}' in repo.refs:
                        base_branch = branch_name
                        break
                except:
                    continue
                    
            logger.info(f"[CODE-ANALYZER] Branch base para comparação: origin/{base_branch}")
            
            # Obter os arquivos modificados comparando com a branch base
            try:
                # Tentar diff direto
                diff = repo.git.diff(f'origin/{base_branch}', '--name-only')
                modified_files = [f for f in diff.split('\n') if f]
                logger.info(f"[CODE-ANALYZER] {len(modified_files)} arquivos modificados encontrados via diff")
                
                # Adicionar arquivos não rastreados (novos)
                untracked_files = repo.untracked_files
                logger.info(f"[CODE-ANALYZER] {len(untracked_files)} arquivos não rastreados encontrados")
                modified_files.extend(untracked_files)
                
                # Filtrar apenas arquivos existentes e não vazios
                modified_files = [
                    f for f in modified_files 
                    if f and os.path.exists(os.path.join(repo_path, f))
                ]
                
                logger.info(f"[CODE-ANALYZER] Total: {len(modified_files)} arquivos para análise")
                
                # Se não encontramos nenhum arquivo, tentar outra abordagem
                if not modified_files:
                    # Tentar listar todos os arquivos recentes (últimas alterações)
                    logger.warning("[CODE-ANALYZER] Nenhum arquivo encontrado via diff, tentando via histórico de commits")
                    # Listar os últimos 10 commits para ver arquivos alterados recentemente
                    recent_commits = list(repo.iter_commits(max_count=10))
                    for commit in recent_commits:
                        for file in commit.stats.files:
                            if os.path.exists(os.path.join(repo_path, file)):
                                modified_files.append(file)
                    # Remover duplicatas
                    modified_files = list(set(modified_files))
                    logger.info(f"[CODE-ANALYZER] {len(modified_files)} arquivos encontrados via histórico de commits")
                
                return modified_files
                
            except Exception as e:
                logger.warning(f"[CODE-ANALYZER] Erro ao buscar diff: {str(e)}")
                # Se falhar, tentar listar apenas os arquivos principais do projeto
                logger.warning("[CODE-ANALYZER] Tentando encontrar arquivos principais do projeto")
                modified_files = []
                for root, _, files in os.walk(repo_path):
                    if '.git' in root:
                        continue
                    for file in files:
                        if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.cpp', '.c')):
                            rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                            modified_files.append(rel_path)
                
                # Limitar a quantidade de arquivos para não sobrecarregar
                if len(modified_files) > 20:
                    logger.warning(f"[CODE-ANALYZER] Muitos arquivos encontrados ({len(modified_files)}), limitando aos 20 primeiros")
                    modified_files = modified_files[:20]
                
                logger.info(f"[CODE-ANALYZER] {len(modified_files)} arquivos selecionados para análise")
                return modified_files
                
        except Exception as e:
            logger.error(f"[CODE-ANALYZER] Erro ao obter arquivos modificados: {str(e)}")
            # Se tudo falhar, retornar uma lista vazia
            return []

    @staticmethod
    def analyze_code(code: str, user_prefer: UserPreferDTO) -> Optional[str]:
        """
        Analisa um trecho específico de código.
        
        Args:
            code: Código a ser analisado
            user_prefer: Preferências do usuário
            
        Returns:
            Optional[str]: Resultado da análise
        """
        try:
            logger.info(f"[CODE-ANALYZER] Iniciando análise de trecho de código: {len(code)} caracteres")
            
            # Inicializar LLM
            llm = LLMGateway()
            
            # Analisar o código
            analysis_result = llm.analyze_code(code)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"[CODE-ANALYZER] Erro ao analisar código: {str(e)}")
            raise
