
class BusinessException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class CredentialsException(Exception):
    def __init__(self, status_code: int, detail: str, headers: dict | None):
        self.status_code = status_code
        self.detail = detail
        self.headers: None = headers


