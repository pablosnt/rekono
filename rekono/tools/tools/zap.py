from tools.tools.base_tool import BaseTool
import xml.etree.ElementTree as parser
from html import unescape
from findings.enums import Severity
from findings.models import Vulnerability, HttpEndpoint
import os


class ZapTool(BaseTool):

    severity_mapping = {
        0: Severity.INFO,
        1: Severity.LOW,
        2: Severity.MEDIUM,
        3: Severity.HIGH
    }

    def clean_value(self, value) -> str:
        value = unescape(value)
        return value.replace('<p>', '').replace('</p>', '')

    def parse_output(self, output: str) -> list:
        findings = []
        endpoints = set()
        if os.path.isfile(self.path_output):
            root = parser.parse(self.path_output).getroot()
            for site in root:
                url_base = site.attrib['name']
                for alert in site.findall('alerts/alertitem'):
                    # TODO: add <cweid>1275</cweid> field to vulnerability
                    vulnerability = Vulnerability.objects.create(
                        name=self.clean_value(alert.findtext('alert')),
                        description=self.clean_value(alert.findtext('desc')),
                        severity=self.severity_mapping[int(alert.findtext('riskcode'))],
                        reference=self.clean_value(alert.findtext('reference'))
                    )
                    findings.append(vulnerability)
                    for instance in alert.findall('instances/instance'):
                        http_endpoint = instance.findtext('uri')
                        if url_base in http_endpoint:
                            http_endpoint = http_endpoint.replace(url_base, '')
                        if http_endpoint == '/':
                            continue
                        if http_endpoint:
                            if http_endpoint[-1] != '/':
                                http_endpoint += '/'
                            if http_endpoint not in endpoints:
                                endpoint = HttpEndpoint.objects.create(endpoint=http_endpoint)
                                findings.append(endpoint)
                                endpoints.add(http_endpoint)
        return findings
