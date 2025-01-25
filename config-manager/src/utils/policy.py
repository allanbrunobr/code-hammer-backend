import os

class Policy:

    @staticmethod
    def origins(app_url:str = None) -> list[str]:
        origins_str = os.getenv("APPLICATION_ORIGINS")
        result = []

        if app_url:
            result.append(app_url)

        if isinstance(origins_str, str):
            result = origins_str.split(", ")

        return result
