from findings.models import HttpEndpoint
from tools.tools.base_tool import BaseTool
import json
import os


class DirsearchTool(BaseTool):

    file_output_enabled = True
    ignore_exit_code = True

    def parse_output(self, output: str) -> list:
        http_endpoints = []
        if os.path.isfile(self.path_output):
            with open(self.path_output) as output_file:
                data = json.load(output_file)
                for url in data.get('results', []):
                    for item in url.values():
                        for endpoint in item:
                            http_endpoint = HttpEndpoint.objects.create(
                                endpoint=endpoint.get('path', ''),
                                status=endpoint.get('status', 0),
                                enumeration=self.url.enumeration if hasattr(self, 'url') else None
                            )
                            http_endpoints.append(http_endpoint)
        return http_endpoints
