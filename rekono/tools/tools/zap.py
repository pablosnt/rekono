import xml.etree.ElementTree as parser
from html import unescape

from findings.enums import Severity
from findings.models import Endpoint, Vulnerability
from tools.tools.base_tool import BaseTool


class ZapTool(BaseTool):
    '''OWASP ZAP tool class.'''

    # Mapping between OWASP ZAP severity values and Rekono severity values
    severity_mapping = {
        0: Severity.INFO,
        1: Severity.LOW,
        2: Severity.MEDIUM,
        3: Severity.HIGH
    }

    def clean_value(self, value: str) -> str:
        '''Clean report values before use it.

        Args:
            value (str): Original value

        Returns:
            str: Clean value
        '''
        value = unescape(value)
        return value.replace('<p>', '').replace('</p>', '')

    def clean_reference(self, value: str) -> str:
        '''Clean reference values because it can contains multiples links.

        Args:
            value (str): Original value

        Returns:
            str: Clean reference value
        '''
        if '</p><p>' in value:
            value = value.split('</p><p>', 1)[0]                                # If multiples links, get the first one
        return self.clean_value(value)

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        http_endpoints = set(['/'])                                             # HTTP endpoints set
        root = parser.parse(self.path_output).getroot()                         # Report root
        for site in root:                                                       # For each site
            url_base = site.attrib['name']                                      # Get target URL
            for alert in site.findall('alerts/alertitem'):                      # For each alert
                name = alert.findtext('alert')                                  # Get alert data
                description = alert.findtext('desc')
                severity = alert.findtext('riskcode')
                cwe = alert.findtext("cweid")
                reference = alert.findtext('reference')
                if name:                                                        # If alert name exists
                    self.create_finding(                                        # Create Vulnerability
                        Vulnerability,
                        name=self.clean_value(name),
                        description=self.clean_value(description) if description else self.clean_value(name),
                        severity=self.severity_mapping[int(severity)] if severity else Severity.MEDIUM,
                        cwe=f'CWE-{cwe}' if cwe else None,
                        reference=self.clean_reference(reference) if reference else None
                    )
                instances = alert.findall('instances/instance')                 # Get instances
                for instance in instances or []:                                # For each instance
                    url = instance.findtext('uri')                              # Get URL
                    if url:
                        http_endpoint = url.replace(url_base, '')               # Get HTTP endpoint
                        if http_endpoint and http_endpoint not in http_endpoints:   # If it's a new endpoint
                            http_endpoints.add(http_endpoint)                   # Add endpoint to HTTP endpoints set
                            self.create_finding(Endpoint, endpoint=http_endpoint)   # Create Endpoint
