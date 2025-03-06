import os

class Policy:

    @staticmethod
    def origins(app_url:str = None) -> list[str]:
        origins_str = os.getenv("APPLICATION_ORIGINS")
        result = []

        if app_url:
            result.append(app_url)
            
        # Adicionar explicitamente a origem do frontend
        result.append("http://localhost:3000")

        if isinstance(origins_str, str):
            if origins_str == "*":
                # Se for configurado para aceitar qualquer origem
                return ["*"]
            else:
                # Adicionar as origens configuradas
                origins = origins_str.split(", ")
                for origin in origins:
                    if origin and origin not in result:
                        result.append(origin)

        return result
