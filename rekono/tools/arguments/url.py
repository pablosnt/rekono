from typing import Any

import requests
from findings.models import Enumeration
from targets.models import Target, TargetPort

HTTP_PORT = 'http://{host}:{port}/'
HTTPS_PORT = 'https://{host}:{port}/'
HTTP_SIMPLE = 'http://{host}/'
HTTPS_SIMPLE = 'https://{host}/'


class Url():

    def __init__(self, host: Target, port: Any) -> None:
        self.value = None
        self.enumeration = None
        if port:
            if isinstance(port, Enumeration):
                if port.service == 'http':
                    self.value = HTTP_PORT.format(host=port.host.address, port=port.port)
                    self.enumeration = port
                elif port.service in ['https', 'ssl/http']:
                    self.value = HTTPS_PORT.format(host=port.host.address, port=port.port)
                    self.enumeration = port
            elif isinstance(port, TargetPort):
                if host.type == Target.TargetType.DOMAIN:
                    if self.check_connection(HTTPS_SIMPLE.format(host=host.target)):
                        self.value = HTTPS_SIMPLE.format(host=host.target)
                    elif self.check_connection(HTTP_SIMPLE.format(host=host.target)):
                        self.value = HTTP_SIMPLE.format(host=host.target)
                else:
                    if (
                        port.port in [80, 3000, 5000, 8000, 8080] and
                        self.check_connection(HTTP_PORT.format(host=host.target, port=port.port))
                    ):
                        self.value = HTTP_PORT.format(host=host.target, port=port.port)
                    elif (
                        port.port in [443, 8443] and
                        self.check_connection(HTTPS_PORT.format(host=host.target, port=port.port))
                    ):
                        self.value = HTTPS_PORT.format(host=host.target, port=port.port)
        else:
            if self.check_connection(HTTPS_SIMPLE.format(host=host.target)):
                self.value = HTTPS_SIMPLE.format(host=host.target)
            elif self.check_connection(HTTP_SIMPLE.format(host=host.target)):
                self.value = HTTP_SIMPLE.format(host=host.target)

    def check_connection(self, url: str) -> bool:
        try:
            requests.get(url)
            return True
        except Exception:
            return False
