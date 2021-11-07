import json

from findings.models import Endpoint
from tools.tools.base_tool import BaseTool


class DirsearchTool(BaseTool):

    ignore_exit_code = True

    def parse_output(self, output: str) -> list:
        http_endpoints = []
        with open(self.path_output) as output_file:
            data = json.load(output_file)
        for url in data.get('results', []):
            for item in url.values():
                for endpoint in item:
                    http_endpoint = Endpoint.objects.create(
                        endpoint=endpoint.get('path', ''),
                        status=endpoint.get('status', 0),
                        enumeration=self.url.enumeration if hasattr(self, 'url') else None
                    )
                    http_endpoints.append(http_endpoint)
        return http_endpoints
