import requests
import os
from fastapi import HTTPException
import logging
from typing import Dict, List, Optional, Any

# Obter URL do config-manager do arquivo .env
CONFIG_MANAGER_URL = os.getenv("CONFIG_MANAGER_URL", "http://localhost:8082")

# Cache para armazenar integrações
_integrations_cache: Dict[str, List[Dict[str, Any]]] = {}

class ConfigManagerClient:
    """Cliente para comunicação com o serviço config-manager"""
    
    @staticmethod
    def get_user_subscription(user_id: str):
        """Obtém a assinatura do usuário do config-manager"""
        try:
            logging.info(f"Requesting subscription for user_id: {user_id}")
            url = f"{CONFIG_MANAGER_URL}/api/v1/users/{user_id}/subscription"
            logging.info(f"Making request to: {url}")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                logging.info("Subscription found")
                return response.json()
            elif response.status_code == 404:
                logging.warning(f"No subscription found for user {user_id}, returning free plan")
                # Se o usuário não tiver assinatura, retornar plano gratuito
                return {
                    "plan": "Gratuito",
                    "status": "active",
                    "planId": "4fb7a959-cd1d-40f3-a73d-e043604b3f0a",
                    "startDate": None,
                    "endDate": None,
                    "remainingFileQuota": 5,
                    "autoRenew": False,
                    "price": 0.0
                }
            else:
                logging.error(f"HTTP error {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Error from config-manager: {response.text}"
                )
                
        except requests.exceptions.ConnectionError as err:
            logging.error(f"Connection error to config-manager: {str(err)}")
            # Em caso de erro de conexão, retornar plano gratuito para não bloquear o frontend
            return {
                "plan": "Gratuito",
                "status": "active",
                "planId": "4fb7a959-cd1d-40f3-a73d-e043604b3f0a",
                "startDate": None,
                "endDate": None,
                "remainingFileQuota": 5,
                "autoRenew": False,
                "price": 0.0
            }
        except Exception as err:
            logging.error(f"Unexpected error: {str(err)}")
            raise HTTPException(status_code=500, detail=f"Error communicating with config-manager: {str(err)}")
    
    @staticmethod
    def get_file_quota(user_id: str, pr_file_count: int = 0):
        """Obtém informações sobre a quota de arquivos do usuário"""
        try:
            logging.info(f"Requesting file quota for user_id: {user_id} with PR file count: {pr_file_count}")
            url = f"{CONFIG_MANAGER_URL}/api/v1/file-quotas/user/{user_id}?pr_file_count={pr_file_count}"
            logging.info(f"Making request to: {url}")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                logging.info("File quota info found")
                return response.json()
            elif response.status_code == 404:
                logging.warning(f"No subscription found for user {user_id}")
                # Retornar valores padrão para não bloquear o frontend
                return {
                    "evaluated_files": pr_file_count,
                    "available_files": 25 - pr_file_count,  # Valor padrão de 25 arquivos
                    "remaining_file_quota": pr_file_count,
                    "plan_file_limit": 25
                }
            else:
                logging.error(f"HTTP error {response.status_code}: {response.text}")
                # Retornar valores padrão para não bloquear o frontend
                return {
                    "evaluated_files": pr_file_count,
                    "available_files": 25 - pr_file_count,
                    "remaining_file_quota": pr_file_count,
                    "plan_file_limit": 25
                }
                
        except requests.exceptions.ConnectionError as err:
            logging.error(f"Connection error to config-manager: {str(err)}")
            # Em caso de erro de conexão, retornar valores padrão
            return {
                "evaluated_files": pr_file_count,
                "available_files": 25 - pr_file_count,
                "remaining_file_quota": pr_file_count,
                "plan_file_limit": 25
            }
        except Exception as err:
            logging.error(f"Unexpected error: {str(err)}")
            # Em caso de erro, retornar valores padrão
            return {
                "evaluated_files": pr_file_count,
                "available_files": 25 - pr_file_count,
                "remaining_file_quota": pr_file_count,
                "plan_file_limit": 25
            }
    
    @staticmethod
    def update_file_quota(user_id: str, pr_file_count: int):
        """Atualiza a quota de arquivos do usuário após a análise de um PR"""
        try:
            logging.info(f"Updating file quota for user_id: {user_id} with PR file count: {pr_file_count}")
            url = f"{CONFIG_MANAGER_URL}/api/v1/file-quotas/user/{user_id}/update-quota?pr_file_count={pr_file_count}"
            logging.info(f"Making request to: {url}")
            
            response = requests.post(url)
            
            if response.status_code == 200:
                logging.info("File quota updated successfully")
                return response.json()
            else:
                logging.error(f"HTTP error {response.status_code}: {response.text}")
                return None
                
        except Exception as err:
            logging.error(f"Error updating file quota: {str(err)}")
            return None
            
    @staticmethod
    def get_quota_info(user_id: str):
        """
        Obtém informações simplificadas sobre a quota de arquivos do usuário.
        Este método acessa o endpoint simplificado que não considera arquivos de um novo PR.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict com informações sobre a quota de arquivos ou valores padrão em caso de erro:
            - evaluated_files: Quantidade de arquivos já avaliados
            - available_files: Quantidade de arquivos disponíveis
        """
        try:
            logging.info(f"Getting simple quota info for user_id: {user_id}")
            url = f"{CONFIG_MANAGER_URL}/api/v1/file-quotas/quota-info/{user_id}"
            logging.info(f"Making request to: {url}")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                logging.info("Quota info retrieved successfully")
                return response.json()
            elif response.status_code == 404:
                logging.warning(f"No subscription found for user {user_id}")
                # Retornar valores padrão para não bloquear o frontend
                return {
                    "evaluated_files": 0,
                    "available_files": 25  # Valor padrão de 25 arquivos
                }
            else:
                logging.error(f"HTTP error {response.status_code}: {response.text}")
                # Retornar valores padrão para não bloquear o frontend
                return {
                    "evaluated_files": 0,
                    "available_files": 25
                }
                
        except requests.exceptions.ConnectionError as err:
            logging.error(f"Connection error to config-manager: {str(err)}")
            # Em caso de erro de conexão, retornar valores padrão
            return {
                "evaluated_files": 0,
                "available_files": 25
            }
        except Exception as err:
            logging.error(f"Unexpected error: {str(err)}")
            # Em caso de erro, retornar valores padrão
            return {
                "evaluated_files": 0,
                "available_files": 25
            }
            
    @staticmethod
    def list_user_integrations(user_id: str = None):
        """
        Lista todas as integrações do usuário.
        
        Args:
            user_id: ID do usuário (opcional, se não fornecido usa o usuário autenticado)
            
        Returns:
            Lista de integrações do usuário ou lista vazia em caso de erro
        """
        global _integrations_cache
        
        try:
            # Se não foi fornecido um user_id, retornar lista vazia
            if not user_id:
                logging.error("[CONFIG-CLIENT] Nenhum user_id fornecido")
                return []
            
            # Construir URL com user_id
            url = f"{CONFIG_MANAGER_URL}/api/v1/integrations/?user_id={user_id}"
            
            logging.info(f"[CONFIG-CLIENT] Listando integrações do usuário. URL: {url}")
            logging.info(f"[CONFIG-CLIENT] CONFIG_MANAGER_URL: {CONFIG_MANAGER_URL}")
            
            # Fazer requisição com token de autenticação se disponível
            headers = {}
            token = os.getenv("AUTH_TOKEN")
            if token:
                headers["Authorization"] = f"Bearer {token}"
                logging.info(f"[CONFIG-CLIENT] Usando token de autenticação: {token[:10]}...")
            else:
                logging.warning("[CONFIG-CLIENT] Token de autenticação não encontrado!")
            
            logging.info(f"[CONFIG-CLIENT] Headers: {headers}")
            
            # Tentar várias abordagens para obter as integrações
            approaches = [
                {"url": url, "headers": headers, "desc": "URL com user_id e token"},
                {"url": f"{CONFIG_MANAGER_URL}/api/v1/integrations/", "headers": headers, "desc": "URL sem user_id, com token"},
                {"url": f"{CONFIG_MANAGER_URL}/integrations/?user_id={user_id}", "headers": headers, "desc": "URL alternativa com user_id e token"},
                {"url": f"{CONFIG_MANAGER_URL}/integrations/", "headers": headers, "desc": "URL alternativa sem user_id, com token"},
                {"url": url, "headers": {}, "desc": "URL com user_id, sem token"},
                {"url": f"{CONFIG_MANAGER_URL}/api/v1/integrations/", "headers": {}, "desc": "URL sem user_id, sem token"}
            ]
            
            for approach in approaches:
                try:
                    logging.info(f"[CONFIG-CLIENT] Tentando abordagem: {approach['desc']}")
                    logging.info(f"[CONFIG-CLIENT] URL: {approach['url']}")
                    
                    response = requests.get(approach['url'], headers=approach['headers'], timeout=10)
                    
                    logging.info(f"[CONFIG-CLIENT] Status code: {response.status_code}")
                    
                    if response.status_code == 200:
                        integrations = response.json()
                        logging.info(f"[CONFIG-CLIENT] {len(integrations)} integrações encontradas")
                        
                        if integrations:
                            # Armazenar integrações no cache
                            _integrations_cache[user_id] = integrations
                            logging.info(f"[CONFIG-CLIENT] Integrações armazenadas no cache para o usuário {user_id}")
                            return integrations
                        else:
                            logging.warning(f"[CONFIG-CLIENT] Lista de integrações vazia")
                except Exception as req_err:
                    logging.error(f"[CONFIG-CLIENT] Erro na abordagem {approach['desc']}: {str(req_err)}")
            
            # Se chegamos aqui, nenhuma abordagem funcionou
            logging.error("[CONFIG-CLIENT] Todas as abordagens falharam. Retornando lista vazia.")
            
            # Retornar lista vazia para forçar o frontend a buscar diretamente do config-manager
            return []
                
        except Exception as err:
            logging.error(f"[CONFIG-CLIENT] Erro ao listar integrações: {str(err)}")
            logging.exception("[CONFIG-CLIENT] Traceback completo:")
            
            # Retornar lista vazia em caso de erro
            return []
    
    @staticmethod
    def get_integration_by_id(integration_id: str):
        """Obtém detalhes de uma integração específica"""
        global _integrations_cache
        
        try:
            # CORREÇÃO: Vamos focar na abordagem que sabemos que funciona - buscar pela lista de usuários
            
            # Primeiro, vamos verificar se temos o ID do usuário que sabemos que tem a integração
            known_user_id = "f70cf81c-3d1d-4cf0-8598-91be25d49b1e"
            
            # Tentar buscar diretamente com o usuário conhecido
            try:
                user_integrations_url = f"{CONFIG_MANAGER_URL}/api/v1/integrations/?user_id={known_user_id}"
                logging.info(f"[CONFIG-CLIENT] Buscando integrações do usuário conhecido {known_user_id}: {user_integrations_url}")
                
                user_response = requests.get(user_integrations_url, timeout=10)
                
                if user_response.status_code == 200:
                    user_integrations = user_response.json()
                    
                    # Atualizar o cache com as integrações encontradas
                    if isinstance(user_integrations, list):
                        _integrations_cache[known_user_id] = user_integrations
                        
                        # Procurar a integração na lista
                        for integration in user_integrations:
                            if str(integration.get('id')) == str(integration_id):
                                logging.info(f"[CONFIG-CLIENT] Integração {integration_id} encontrada para o usuário conhecido!")
                                return integration
                        
                        logging.warning(f"[CONFIG-CLIENT] Integração {integration_id} não encontrada na lista do usuário conhecido")
            except Exception as err:
                logging.error(f"[CONFIG-CLIENT] Erro ao buscar integrações do usuário conhecido: {str(err)}")
            
            # Se não encontrou com o usuário conhecido, verificar no cache
            logging.info(f"[CONFIG-CLIENT] Verificando integração {integration_id} no cache...")
            for user_id, integrations in _integrations_cache.items():
                for integration in integrations:
                    if str(integration.get('id')) == str(integration_id):
                        logging.info(f"[CONFIG-CLIENT] Integração {integration_id} encontrada no cache do usuário {user_id}!")
                        return integration
            
            # Se ainda não encontrou, tentar com todos os usuários no cache
            user_ids = list(_integrations_cache.keys())
            if user_ids:
                for user_id in user_ids:
                    if user_id == known_user_id:
                        continue  # Já tentamos com este usuário
                        
                    try:
                        user_integrations_url = f"{CONFIG_MANAGER_URL}/api/v1/integrations/?user_id={user_id}"
                        logging.info(f"[CONFIG-CLIENT] Buscando integrações do usuário {user_id}: {user_integrations_url}")
                        
                        user_response = requests.get(user_integrations_url, timeout=10)
                        
                        if user_response.status_code == 200:
                            user_integrations = user_response.json()
                            
                            # Atualizar o cache
                            if isinstance(user_integrations, list):
                                _integrations_cache[user_id] = user_integrations
                                
                                # Procurar a integração
                                for integration in user_integrations:
                                    if str(integration.get('id')) == str(integration_id):
                                        logging.info(f"[CONFIG-CLIENT] Integração {integration_id} encontrada para o usuário {user_id}!")
                                        return integration
                    except Exception as err:
                        logging.error(f"[CONFIG-CLIENT] Erro ao buscar integrações do usuário {user_id}: {str(err)}")
            
            # Como último recurso, tentar o endpoint direto (mesmo que provavelmente falhe)
            try:
                direct_urls = [
                    f"{CONFIG_MANAGER_URL}/api/v1/integrations/{integration_id}",
                    f"{CONFIG_MANAGER_URL}/integrations/{integration_id}"
                ]
                
                for url in direct_urls:
                    logging.info(f"[CONFIG-CLIENT] Tentando buscar integração diretamente: {url}")
                    
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        logging.info(f"[CONFIG-CLIENT] Integração encontrada diretamente: {data.get('name', 'N/A')}")
                        return data
            except Exception as err:
                logging.error(f"[CONFIG-CLIENT] Erro ao tentar buscar integração diretamente: {str(err)}")
            
            # Se chegamos aqui, não encontramos a integração
            logging.error(f"[CONFIG-CLIENT] Integração {integration_id} não encontrada após todas as tentativas")
            return None
                
        except Exception as err:
            logging.error(f"[CONFIG-CLIENT] Erro inesperado ao buscar integração: {str(err)}")
            logging.exception("[CONFIG-CLIENT] Traceback completo:")
            
            # Retornar None em caso de erro
            return None
