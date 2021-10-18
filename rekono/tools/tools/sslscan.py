from tools.tools.base_tool import BaseTool
import xml.etree.ElementTree as parser
from findings.models import Vulnerability, Technology
from findings.enums import Severity
import os


class SslscanTool(BaseTool):

    def get_technology(self, technologies, sslversion):
        select = [tech for tech in technologies if f'{tech.name}v{tech.version}' == sslversion]
        if select:
            return select[0]

    def parse_output(self, output: str) -> list:
        technologies = []
        vulnerabilities = []
        if os.path.isfile(self.path_output):
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
                                    item.attrib['type'] == 'tls' and
                                    item.attrib['version'] not in ['1.2', '1.3']
                                ) or 
                                item.attrib['type'] == 'ssl'
                            ) and item.attrib['enabled'] == '1'
                        ):
                            vulnerability = Vulnerability.objects.create(
                                technology=technology,
                                name=f'Insecure {item.attrib["type"].upper()} version supported',
                                description=f'{item.attrib["type"].upper()} {item.attrib["version"]} is supported',
                                severity=Severity.LOW if item.attrib["type"] == 'tls' else Severity.MEDIUM
                            )
                            vulnerabilities.append(vulnerability)
                    elif (
                        item.tag == 'renegotiation' and
                        item.attrib['supported'] == '1' and
                        item.attrib['secure'] != '1'
                    ):
                        vulnerability = Vulnerability.objects.create(
                            name='Insecure SSL renegotiation supported',
                            description='Insecure SSL renegotiation supported',
                            severity=Severity.MEDIUM
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
                        item.tag == 'cipher' and
                        item.attrib['strength'] not in ['acceptable', 'strong']
                    ):
                        vulnerability = Vulnerability.objects.create(
                            technology=self.get_technology(technologies, item.attrib['sslversion']),
                            name='Insecure cipher suite supported',
                            description=f'{item.attrib["sslversion"]} {item.attrib["cipher"]} status={item.attrib["status"]} strength={item.attrib["strength"]}',
                            severity=Severity.LOW
                        )
                        vulnerabilities.append(vulnerability)
        return technologies + vulnerabilities
