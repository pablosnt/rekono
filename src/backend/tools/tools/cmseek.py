import json
import os
import shutil
from typing import Any
from urllib.parse import urlparse

from findings.enums import PathType, Severity
from findings.models import Credential, Path, Technology, Vulnerability
from tools.tools.base_tool import BaseTool

from rekono.settings import TOOLS


class Cmseek(BaseTool):
    '''CMSeeK tool class.'''

    # CMSeeK directory where output files can be stored
    home_directory = TOOLS['cmseek']['directory']

    def clean_environment(self) -> None:
        '''Move original file output to Rekono outputs directory.'''
        # Get path from URL used in command
        url_path = self.get_host_from_url('-u').replace('/', '_').replace(':', '_')
        report_file = 'cms.json'                                                # Original output file name
        results = os.path.join('Result', url_path)                              # Result path in current directory
        # Original output file in current directory
        report = os.path.join(results, report_file)
        home_results = os.path.join(self.home_directory, results)               # Result path in CMSeeK directory
        # Original output file in CMSeeK directory
        home_report = os.path.join(home_results, report_file)
        if not os.path.isfile(report) and os.path.isfile(home_report):          # If output file in CMSeeK directory
            results = home_results                                              # Update results path variable
            report = home_report                                                # Update report path variable
        if os.path.isfile(report):                                              # If report file found
            # Move original report file to Rekono outputs directory
            shutil.move(report, self.path_output)
            shutil.rmtree(results)                                              # Remove results directory

    def analyze_endpoints(self, url: str, technology: Technology, key: str, value: Any) -> None:
        '''Analyze endpoints from report item.

        Args:
            url (str): Target URL
            technology (Technology): Technology created from basic CMS data
            key (str): Item key
            value (Any): Item value
        '''
        paths = value
        if isinstance(value, str):
            paths = value.split(',') if ',' in value else [value]               # Paths from string value
        # Remove target URL from paths
        paths = [p.replace(url, '/') for p in paths if p and p.replace(url, '/') != '/']
        for path in paths:                                                      # For each path
            # Create Path
            self.create_finding(Path, path=path.replace('//', '/'), type=PathType.ENDPOINT)
        if 'backup_file' in key:                                                # Backup file found
            self.create_finding(                                                # Create Vulnerability
                Vulnerability,
                technology=technology,
                name='Backup files found',
                description=', '.join(paths),
                severity=Severity.HIGH,
                # CWE-530: Exposure of Backup File to an Unauthorized Control Sphere
                cwe='CWE-530'
            )
        elif 'config_file' in key:                                              # Configuration file found
            self.create_finding(
                Vulnerability,
                technology=technology,
                name='Configuration files found',
                description=', '.join(paths),
                severity=Severity.MEDIUM,
                # CWE-497: Exposure of Sensitive System Information to an Unauthorized Control Sphere
                cwe='CWE-497'
            )

    def parse_cms_components(self, key: str, value: str, cms_name: str, cms_id: str, cms: Technology) -> None:
        '''Parse CMS components data to create Technologies.

        Args:
            key (str): Component key
            value (str): Component value
            cms_name (str): CMS name
            cms_id (str): CMS Id
            cms (Technology): CMS Technology
        '''
        for item in value.split(','):                                           # For each CMS component
            aux = item.split('Version', 1)                                      # Parse component data
            name = None
            if cms_name in key:
                name = key.replace(f'{cms_name}_', '')                          # Get CMS component type name
            elif cms_id in key:
                name = key.replace(f'{cms_id}_', '')                            # Get CMS component type name
            tech = aux[0].strip() if len(aux) > 0 else None                     # Get CMS component name
            vers = aux[1].strip() if len(aux) > 1 else None                     # Get CMS component version
            if tech:                                                            # If CMS component name found
                # Create Technology with CMS component data
                self.create_finding(
                    Technology,
                    name=tech,
                    version=vers,
                    related_to=cms,                                             # Related to CMS technology
                    description=f'{cms_name} {name}'
                )

    def parse_cms_vulnerabilities(self, value: dict, cms: Technology) -> None:
        '''Parse CMS vulnerabilities to create Vulnerabilities.

        Args:
            value (dict): Vulnerability values
            cms (Technology): CMS Technology
        '''
        for vuln in value['vulnerabilities']:                                   # For each CVE
            # Create Vulnerability with CVE and related to CMS Technology
            self.create_finding(Vulnerability, technology=cms, name=vuln.get('name'), cve=vuln.get('cve'))

    def parse_cms_usernames(self, value: str, cms: Technology) -> None:
        '''Parse CMS usernames to create Credentials.

        Args:
            value (str): Username values
            cms (Technology): CMS Technology
        '''
        for user in value.split(','):                                           # For each username
            if user:
                self.create_finding(                                            # Create Credential with username
                    Credential,
                    technology=cms,
                    username=user,
                    context=f'{cms.name} username'
                )

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        with open(self.path_output, 'r', encoding='utf-8') as output_file:
            report = json.load(output_file)                                     # Read output file
        cms_name = report.get('cms_name')                                       # Get CMS name
        cms_id = report.get('cms_id')                                           # Get CMS Id
        if cms_name and cms_id:                                                 # CMS found
            cms_version = None
            if f'{cms_id}_version' in report:                                   # Search CMS version by Id
                cms_version = report.get(f'{cms_id}_version')                   # Get CMS version by Id
            elif f'{cms_name}_version' in report:                               # Search CMS version by name
                cms_version = report.get(f'{cms_name}_version')                 # Get CMS version by name
            url = report.get('url')                                             # Get target URL
            if url:
                url_parsed = urlparse(report.get('url'))                        # Parse target URL
                if url_parsed.path:                                             # Path in the target URL
                    url = url.replace(url_parsed.path, '/')                     # Remove endpoint from the base URL
            cms = self.create_finding(                                          # Create Technology with the CMS data
                Technology,
                name=cms_name,
                version=cms_version,
                description='CMS',
                reference=report.get('cms_url')
            )
            for key, value in [(k, v) for k, v in report.items() if k not in [  # For each data in report
                'cms_id', 'cms_name', 'cms_url',                                # Exclude basic CMS data
                f'{cms_id}_version', f'{cms_name}_version', 'url'
            ]]:
                if (
                    (isinstance(value, str) and url in value) or
                    (isinstance(value, list) and len([i for i in value if url in i]) > 0)
                ):
                    # Path found
                    self.analyze_endpoints(url, cms, key, value)                # Analyze endpoint
                elif '_users' in key and ',' in value:                          # Users found
                    self.parse_cms_usernames(value, cms)
                elif '_debug_mode' in key and value != 'disabled':              # Vulnerability found: debug enabled
                    self.create_finding(                                        # Create Vulnerability
                        Vulnerability,
                        technology=cms,                                         # Related to CMS technology
                        name='Debug mode enabled',
                        description=f'{cms_name} debug mode enabled',
                        severity=Severity.LOW,
                        cwe='CWE-489'                                           # CWE-489: Active Debug Code
                    )
                elif '_vulns' in key and 'vulnerabilities' in value:            # CVEs found
                    self.parse_cms_vulnerabilities(value, cms)                  # Parse CMS vulnerabilities
                elif 'Version' in value and ',' in value:
                    # CMS component found (plugin, theme, ...)
                    self.parse_cms_components(key, value, cms_name, cms_id, cms)    # Parse CMS components
