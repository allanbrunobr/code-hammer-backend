import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_config_manager_endpoint():
    """
    Test the diagnostics/quota endpoint on config-manager.
    """
    try:
        # Make a request to the config-manager endpoint
        url = "http://localhost:8082/api/v1/file-quotas/diagnostics/quota?pr_file_count=0"
        logging.info(f"Making request to config-manager: {url}")
        
        response = requests.get(url)
        
        logging.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logging.info("Request to config-manager successful!")
            logging.info(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            logging.error(f"Request to config-manager failed with status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error making request to config-manager: {str(e)}")
        return False

def test_code_analyzer_endpoint():
    """
    Test the diagnostics/quota endpoint on code-analyzer.
    """
    try:
        # Make a request to the code-analyzer endpoint
        url = "http://localhost:8083/api/v1/file-quotas/diagnostics/quota?pr_file_count=0"
        logging.info(f"Making request to code-analyzer: {url}")
        
        # Add a dummy token for authentication
        headers = {"Authorization": "Bearer dummy-token"}
        
        response = requests.get(url, headers=headers)
        
        logging.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logging.info("Request to code-analyzer successful!")
            logging.info(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            logging.error(f"Request to code-analyzer failed with status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error making request to code-analyzer: {str(e)}")
        return False

def handle_error(user_id, pr_file_count=0):
    """
    Handle the 'NoneType' object is not subscriptable error.
    """
    try:
        # Simulate the ConfigManagerClient.get_file_quota method
        logging.info(f"Simulating get_file_quota for user_id: {user_id} with PR file count: {pr_file_count}")
        
        # Return default values
        quota_info = {
            "evaluated_files": pr_file_count,
            "available_files": 25 - pr_file_count,
            "diagnostics": {
                "status": "default_values",
                "message": "Using default values because real data could not be retrieved from the database"
            }
        }
        
        logging.info(f"Returning default values: {json.dumps(quota_info, indent=2)}")
        return quota_info
    except Exception as e:
        logging.error(f"Error in handle_error: {str(e)}")
        # In case of error, return even more basic default values
        return {
            "evaluated_files": 0,
            "available_files": 25,
            "diagnostics": {
                "status": "error",
                "message": f"Error handling error: {str(e)}"
            }
        }

if __name__ == "__main__":
    # Test the config-manager endpoint
    logging.info("Testing config-manager endpoint...")
    config_manager_result = test_config_manager_endpoint()
    
    # Test the code-analyzer endpoint
    logging.info("\nTesting code-analyzer endpoint...")
    code_analyzer_result = test_code_analyzer_endpoint()
    
    if not config_manager_result or not code_analyzer_result:
        # If either test fails, demonstrate the error handling
        logging.info("\nDemonstrating error handling:")
        result = handle_error("test-user-id", 5)
        logging.info(f"Error handling result: {json.dumps(result, indent=2)}")
