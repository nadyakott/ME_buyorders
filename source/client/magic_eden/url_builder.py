from yarl import URL
from typing import Dict, Any

class UrlBuilder:

    @classmethod
    def get_url(cls, base_url: str, api_endpoint: str, params: Dict[str, Any]) -> str:
        return str(URL(base_url).with_path(api_endpoint).with_query(params))