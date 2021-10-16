import csv
import os

from findings.models import HttpEndpoint, Vulnerability
from tools.tools.base_tool import BaseTool
from findings.enums import Severity
import xml.etree.ElementTree as parser


class NiktoTool(BaseTool):

    file_output_enabled = True
    ignore_exit_code = True

    def parse_output(self, output: str) -> list:
        findings = []
        http_endpoints = set()
        if os.path.isfile(self.path_output):
            root = parser.parse(self.path_output).getroot()
            items = root.findall('niktoscan')[-1].findall('scandetails')[0].findall('item')
            for item in items:
                osvdb = int(item.attrib['osvdbid'])
                method = item.attrib['method']
                description = item.find('description').text
                name = description
                if osvdb:
                    name = osvdb
                endpoint = item.find('uri').text
                if '<![DATA[' in endpoint:
                    endpoint = endpoint.split('<![DATA[', 1)[1].rsplit(']]>', 1)[0]
                if description:
                    vulnerability = Vulnerability.objects.create(
                        name=name,
                        description=f'[{method} {endpoint}] {description}',
                        severity=Severity.LOW,
                        osvdb=osvdb
                    )
                    findings.append(vulnerability)
                if endpoint and endpoint not in http_endpoints:
                    http_endpoints.add(endpoint)
                    http_endpoint = HttpEndpoint.objects.create(endpoint=endpoint)
                    findings.append(http_endpoint)
        return findings
