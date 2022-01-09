import xml.etree.ElementTree as parser

from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tools.tools.base_tool import BaseTool


class SslscanTool(BaseTool):

    def get_technology(self, technologies, sslversion):
        select = [tech for tech in technologies if f'{tech.name}v{tech.version}' == sslversion]
        if select:
            return select[0]

    def parse_output(self, output: str) -> None:
        technologies = []
        root = parser.parse(self.path_output).getroot()
        tests = root.findall('ssltest')
        for test in tests:
            for item in test:
                if item.tag == 'protocol':
                    technology = self.create_finding(
                        Technology,
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
                        self.create_finding(
                            Vulnerability,
                            technology=technology,
                            name=f'Insecure {item.attrib["type"].upper()} version supported',
                            description=desc,
                            severity=Severity.MEDIUM,
                            cwe='CWE-326'
                        )
                elif (
                    item.tag == 'renegotiation'
                    and item.attrib['supported'] == '1'
                    and item.attrib['secure'] != '1'
                ):
                    self.create_finding(
                        Vulnerability,
                        technology=self.get_technology(technologies, item.attrib['sslversion']),
                        name='Insecure TLS renegotiation supported',
                        description='Insecure TLS renegotiation supported',
                        severity=Severity.MEDIUM,
                        cwe='CWE-264'
                    )
                elif item.tag == 'heartbleed' and item.attrib['vulnerable'] == '1':
                    self.create_finding(
                        Vulnerability,
                        technology=self.get_technology(technologies, item.attrib['sslversion']),
                        name=f'Heartbleed in {item.attrib["sslversion"]}',
                        cve='CVE-2014-0160',
                    )
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
                    self.create_finding(
                        Vulnerability,
                        technology=self.get_technology(technologies, item.attrib['sslversion']),
                        name='Insecure cipher suite supported',
                        description=desc,
                        severity=Severity.LOW,
                        cwe='CWE-326'
                    )
