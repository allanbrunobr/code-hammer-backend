import base64

class Checkers:

    @staticmethod
    def is_base64(string: str) -> bool:
        try:
            return base64.b64encode(base64.b64decode(string)) == string.encode()
        except Exception:
            return False
