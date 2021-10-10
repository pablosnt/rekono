import csv
import os

from findings.models import HttpEndpoint, Vulnerability
from tools.tools.base_tool import BaseTool
from findings.enums import Severity


class NiktoTool(BaseTool):

    file_output_enabled = True
    ignore_exit_code = True

    def parse_output(self, output: str) -> list:
        findings = []
        http_endpoints = set()
        if os.path.isfile(self.path_output):
            with open(self.path_output) as output_file:
                reader = csv.reader(output_file, delimiter=',')
                for row in reader:
                    if len(row) < 7:
                        continue
                    if row[5] and row[5] not in http_endpoints:
                        http_endpoints.add(row[5])
                        http_endpoint = HttpEndpoint.objects.create(
                            endpoint=row[5]
                        )
                        findings.append(http_endpoint)
                    if row[3] and row[6]:
                        vulnerability = Vulnerability.objects.create(
                            name=row[3],
                            description=f'[{row[4]} {row[5]}] {row[6]}',
                            severity=Severity.INFO,
                            osvdb=row[3]
                        )
                        findings.append(vulnerability)
        return findings
