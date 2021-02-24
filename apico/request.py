from typing import Optional


class Request:
    def __init__(self, url: str,
                 rate: float,
                 headers: Optional[dict] = None,
                 body: Optional[dict] = None,
                 method: str = 'get'):
        self.url: str = url
        self.rate: float = rate
        self.headers: Optional[dict] = headers
        self.body: Optional[dict] = body
        self.method: str = method
