from typing import Optional

import requests

URL_FORMATS = [
    '{protocol}://{host}:{port}/{endpoint}',
    '{protocol}://{host}/{endpoint}'
]


def get_url(host: str, port: int = 0, endpoint: str = '', https: bool = None) -> Optional[str]:
    protocols = ['http', 'https']
    if https is not None:
        protocols = ['https'] if https else ['http']
    for url in URL_FORMATS:
        for protocol in protocols:
            url_to_test = url.format(protocol=protocol, host=host, port=port, endpoint=endpoint)
            if check_connection(url_to_test):
                return url_to_test


def check_connection(url: str) -> bool:
    try:
        requests.get(url)
        return True
    except Exception:
        return False
