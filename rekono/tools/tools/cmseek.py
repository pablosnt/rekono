import json
import os
import shutil

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
        try:
            url = formatter.argument_with_target_ports('{url}', self.target_ports, self.target)
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

    def parse_output(self, output: str) -> list:
        findings = []
        if os.path.isfile(self.path_output):
            with open(self.path_output, 'r') as output:
                report = json.load(output)
            if 'cms_name' in report and report['cms_name']:
                cms_id = report.get('cms_id')
                cms_name = report.get('cms_name')
                cms_reference = report.get('cms_url')
                cms_version = None
                if f'{cms_id}_version' in report:
                    cms_version = report.get(f'{cms_id}_version')
                elif f'{cms_name}_version' in report:
                    cms_version = report.get(f'{cms_name}_version')
                url = report.get('url')
                cms = Technology.objects.create(
                    name=cms_name,
                    version=cms_version,
                    reference=cms_reference
                )
                findings.append(cms)
                for key, value in report.items():
                    if key in ['cms_id', 'cms_name', 'cms_url', f'{cms_id}_version', f'{cms_name}_version']:
                        continue
                    if 'file' in key or 'directory' in key:
                        paths = []
                        if isinstance(value, str) and ',' in value:
                            paths = value.split(',')
                        elif isinstance(value, list):
                            paths = value
                        paths = [p.replace(url, '/') for p in paths]
                        for path in paths:
                            endpoint = Endpoint.objects.create(endpoint=path)
                            findings.append(endpoint)
                        if 'backup_file' in key:
                            vulnerability = Vulnerability.objects.create(
                                name=f'{cms_name} backup files found',
                                description=', '.join(paths),
                                severity=Severity.HIGH,
                                cwe='CWE-530'
                            )
                            findings.append(vulnerability)
                        elif 'config_file' in key:
                            vulnerability = Vulnerability.objects.create(
                                name=f'{cms_name} configuration files found',
                                description=', '.join(paths),
                                severity=Severity.MEDIUM,
                                cwe='CWE-497'
                            )
                            findings.append(vulnerability)
                    elif '_users' in key:
                        if ',' in value:
                            for user in value.split(','):
                                credential = Credential.objects.create(username=user)
                                findings.append(credential)
                    elif '_debug_mode' in key and value != 'disabled':
                        vulnerability = Vulnerability.objects.create(
                            name=f'{cms_name} debug mode enabled',
                            description=f'{cms_name} debug mode enabled',
                            severity=Severity.LOW,
                            cwe='CWE-489'
                        )
                        findings.append(vulnerability)
                    elif '_vulns' in key and 'vulnerabilities' in value:
                        for vuln in value['vulnerabilities']:
                            vulnerability = Vulnerability.objects.create(
                                name=vuln.get('name'),
                                cve=vuln.get('cve')
                            )
                            findings.append(vulnerability)
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
                                technology = Technology.objects.create(
                                    name=tech,
                                    version=vers,
                                    related_to=cms,
                                    description=f'{cms_name} {name}'
                                )
                                findings.append(technology)
        return findings
