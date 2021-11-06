import os
import xml.etree.ElementTree as parser

from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tools.tools.base_tool import BaseTool


class SslscanTool(BaseTool):

    def get_technology(self, technologies, sslversion):
        select = [tech for tech in technologies if f'{tech.name}v{tech.version}' == sslversion]
        if select:
            return select[0]

    def parse_output(self, output: str) -> list:
        technologies = []
        vulnerabilities = []
        root = parser.parse(self.path_output).getroot()
        tests = root.findall('ssltest')
        for test in tests:
            for item in test:
                if item.tag == 'protocol':
                    technology = Technology.objects.create(
                        name=item.attrib['type'].upper(),
                        version=item.attrib['version']
                    )
                    technologies.append(technology)
                    if (
                        (
                            (
                                item.attrib['type'] == 'tls'
                                and item.attrib['version'] not in ['1.2', '1.3']
                            )
                            or item.attrib['type'] == 'ssl'
                        )
                        and item.attrib['enabled'] == '1'
                    ):
                        desc = '{protocol} {version} is supported'.format(
                            protocol=item.attrib["type"].upper(),
                            version=item.attrib["version"]
                        )
                        vulnerability = Vulnerability.objects.create(
                            technology=technology,
                            name=f'Insecure {item.attrib["type"].upper()} version supported',
                            description=desc,
                            severity=Severity.MEDIUM,
                            cwe='CWE-326'
                        )
                        vulnerabilities.append(vulnerability)
                elif (
                    item.tag == 'renegotiation'
                    and item.attrib['supported'] == '1'
                    and item.attrib['secure'] != '1'
                ):
                    vulnerability = Vulnerability.objects.create(
                        name='Insecure TLS renegotiation supported',
                        description='Insecure TLS renegotiation supported',
                        severity=Severity.MEDIUM,
                        cwe='CWE-264'
                    )
                    vulnerabilities.append(vulnerability)
                elif item.tag == 'heartbleed' and item.attrib['vulnerable'] == '1':
                    vulnerability = Vulnerability.objects.create(
                        technology=self.get_technology(technologies, item.attrib['sslversion']),
                        name=f'Heartbleed in {item.attrib["sslversion"]}',
                        cve='CVE-2014-0160',
                    )
                    vulnerabilities.append(vulnerability)
                elif (
                    item.tag == 'cipher'
                    and item.attrib['strength'] not in ['acceptable', 'strong']
                ):
                    desc = '{version} {cipher} status={status} strength={strength}'.format(
                        version=item.attrib["sslversion"],
                        cipher=item.attrib["cipher"],
                        status=item.attrib["status"],
                        strength=item.attrib["strength"]
                    )
                    vulnerability = Vulnerability.objects.create(
                        technology=self.get_technology(technologies, item.attrib['sslversion']),
                        name='Insecure cipher suite supported',
                        description=desc,
                        severity=Severity.LOW,
                        cwe='CWE-326'
                    )
                    vulnerabilities.append(vulnerability)
        return technologies + vulnerabilities
