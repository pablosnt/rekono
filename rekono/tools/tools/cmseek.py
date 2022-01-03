import json
import os
import shutil
from typing import Any

from arguments import formatter
from findings.enums import Severity
from findings.models import Credential, Endpoint, Technology, Vulnerability
from tools.tools.base_tool import BaseTool

from rekono.settings import TOOLS


class CmseekTool(BaseTool):

    home_directory = TOOLS['cmseek']['directory']

    def clean_url(self, url) -> str:
        if '://' in url:
            url = url.split('://', 1)[1]
        if url[-1] == '/':
            url = url[:-1]
        url = url.replace('/', '_').replace(':', '_')
        return url

    def get_url_path(self) -> str:
        for key, value in self.findings_relations:
            try:
                url = formatter.argument_with_one('{url}', value)
                if url:
                    return self.clean_url(url)
            except KeyError:
                pass

    def clean_environment(self) -> None:
        url_path = self.get_url_path()
        report_file = 'cms.json'
        results = os.path.join('Result', url_path)
        report = os.path.join(results, report_file)
        home_results = os.path.join(self.home_directory, results)
        home_report = os.path.join(home_results, report_file)
        if not os.path.isfile(report) and os.path.isfile(home_report):
            results = home_results
            report = home_report
        if os.path.isfile(report):
            shutil.move(report, self.path_output)
            shutil.rmtree(results)

    def analyze_endpoints(self, url: str, technology: Technology, key: str, value: Any) -> None:
        paths = []
        if isinstance(value, str) and ',' in value:
            paths = value.split(',')
        elif isinstance(value, list):
            paths = value
        paths = [p.replace(url, '/') for p in paths]
        for path in paths:
            self.create(Endpoint, endpoint=path)
        if 'backup_file' in key:
            self.create_finding(
                Vulnerability,
                technology=technology,
                name=f'{technology.name} backup files found',
                description=', '.join(paths),
                severity=Severity.HIGH,
                cwe='CWE-530'
            )
        elif 'config_file' in key:
            self.create_finding(
                Vulnerability,
                technology=technology,
                name=f'{technology.name} configuration files found',
                description=', '.join(paths),
                severity=Severity.MEDIUM,
                cwe='CWE-497'
            )

    def parse_output(self, output: str) -> None:
        with open(self.path_output, 'r') as output_file:
            report = json.load(output_file)
        if report.get('cms_name'):
            cms_id = report.get('cms_id')
            cms_name = report.get('cms_name')
            cms_version = None
            if f'{cms_id}_version' in report:
                cms_version = report.get(f'{cms_id}_version')
            elif f'{cms_name}_version' in report:
                cms_version = report.get(f'{cms_name}_version')
            url = report.get('url')
            cms = self.create_finding(
                Technology,
                name=cms_name,
                version=cms_version,
                reference=report.get('cms_url')
            )
            for key, value in [(k, v) for k, v in report.items() if k not in [
                'cms_id', 'cms_name', 'cms_url', f'{cms_id}_version', f'{cms_name}_version'
            ]]:
                if 'file' in key or 'directory' in key:
                    self.analyze_endpoints(url, cms, key, value)
                elif '_users' in key and ',' in value:
                    for user in value.split(','):
                        self.create_finding(Credential, username=user)
                elif '_debug_mode' in key and value != 'disabled':
                    self.create(
                        Vulnerability,
                        technology=cms,
                        name=f'{cms_name} debug mode enabled',
                        description=f'{cms_name} debug mode enabled',
                        severity=Severity.LOW,
                        cwe='CWE-489'
                    )
                elif '_vulns' in key and 'vulnerabilities' in value:
                    for vuln in value['vulnerabilities']:
                        self.create(
                            Vulnerability,
                            technology=cms,
                            name=vuln.get('name'),
                            cve=vuln.get('cve')
                        )
                elif 'Version' in value and ',' in value:
                    for item in value.split(','):
                        aux = item.split('Version', 1)
                        name = None
                        if cms_name in key:
                            name = key.replace(f'{cms_name}_', '')
                        elif cms_id in key:
                            name = key.replace(f'{cms_id}_', '')
                        tech = aux[0].strip() if len(aux) > 0 else None
                        vers = aux[1].strip() if len(aux) > 1 else None
                        if tech:
                            self.create_finding(
                                Technology,
                                name=tech,
                                version=vers,
                                related_to=cms,
                                description=f'{cms_name} {name}'
                            )
