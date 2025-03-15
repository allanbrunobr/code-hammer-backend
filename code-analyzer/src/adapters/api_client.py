import concurrent.futures
import requests
import json
from typing import Callable, Optional, Any, List
from pydantic import BaseModel
from requests.auth import AuthBase

class APIClient:

    class Callback(BaseModel):
        uri: str
        func: Optional[Callable] = None
        args: Optional[Any] = {}

    def __init__(self, base_url: str, auth: AuthBase = None):
        self.base_url = base_url
        self.auth = auth
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def request(self, method: str, endpoint: str, **kwargs) -> Any:
        url = f"{self.base_url}{endpoint}"
        res = requests.request(
            method, 
            url,
            headers=self.headers,
            auth=self.auth,
            **kwargs
        )

        res.raise_for_status()

        return res.json()

    def get(self, endpoint: str, **kwargs) -> Any:
        result = self.request("GET", endpoint=endpoint, **kwargs)

        return result

    def put(self, endpoint: str, data: any, **kwargs) -> Any:
        result = self.request("PUT", endpoint=endpoint, data=json.dumps(data), **kwargs)

        return result

    def post(self, endpoint: str, data: Any, **kwargs) -> Any:
        result = self.request("POST", endpoint=endpoint, data=json.dumps(data), **kwargs)

        return result

    def delete(self, endpoint: str, **kwargs) -> Any:
        result = self.request("DELETE", endpoint=endpoint, **kwargs)

        return result

    def request_all(self, method: str, endpoints: List[str|Callback], **kwargs):
        results = []
        endpoints = [self.Callback(uri=uri) if isinstance(uri, str) else uri for uri in endpoints]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_uri = {executor.submit(self.request, method=method, endpoint=endpoint.uri, **kwargs): endpoint for endpoint in endpoints}

            for future in concurrent.futures.as_completed(future_to_uri):
                call = future_to_uri[future]

                try:
                    data = future.result()

                    if call.func is not None:
                        call.func(data, **call.args)

                    if data is not None:
                        results.append(data)

                except Exception as exc:
                    print(f"{call.uri} gerou uma exceção: {exc}")

        return results
