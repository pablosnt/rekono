from typing import Any, Optional

import requests
from findings.models import Enumeration
from targets.models import TargetPort

HTTP_PORT = 'http://{host}:{port}'
HTTPS_PORT = 'https://{host}:{port}'
HTTP_SIMPLE = 'http://{host}'
HTTPS_SIMPLE = 'https://{host}'


def get_url(host: str, port: Any) -> Optional[str]:
    if port and isinstance(port, Enumeration):
        if port.service == 'http':
            return HTTP_PORT.format(host=port.host.address, port=port.port)
        elif port.service in ['https', 'ssl/http']:
            return HTTPS_PORT.format(host=port.host.address, port=port.port)
    elif port and isinstance(port, TargetPort):
        if check_connection(HTTP_PORT.format(host=host, port=port.port)):
            return HTTP_PORT.format(host=host, port=port.port)
        elif check_connection(HTTPS_PORT.format(host=host, port=port.port)):
            return HTTPS_PORT.format(host=host, port=port.port)
    if check_connection(HTTPS_SIMPLE.format(host=host)):
        return HTTPS_SIMPLE.format(host=host)
    elif check_connection(HTTP_SIMPLE.format(host=host)):
        return HTTP_SIMPLE.format(host=host)
    return None


def check_connection(url: str) -> bool:
    try:
        requests.get(url)
        return True
    except Exception:
        return False
