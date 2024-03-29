from django.apps import AppConfig
from framework.apps import BaseApp


class HttpHeadersConfig(BaseApp, AppConfig):
    name = "http_headers"
