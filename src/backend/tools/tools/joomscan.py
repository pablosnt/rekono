from findings.enums import PathType, Severity
from findings.models import Exploit, Path, Technology, Vulnerability
from tools.tools.base_tool import BaseTool


class Joomscan(BaseTool):
    '''JoomScan tool class.'''

    def parse_plain_output(self, output: str) -> None:
        '''Parse tool plain output to create finding entities. This should be implemented by child tool classes.

        Args:
            output (str): Plain tool output
        '''
        technology = None
        vulnerability_name = None
        endpoints = ['/']
        backups = []
        configurations = []
        path_disclosure = []
        directory_listing = []
        host = self.get_host_from_url('-u')                                     # Get host associated to the target URL
        lines = output.split('\n')
        for index, line in enumerate(lines):                                    # For each line
            data = line.strip()
            if not data:
                continue
            if '[++] Joomla' in data and lines[index - 1] == '[+] Detecting Joomla Version':    # Joomla version found
                version = data.replace('[++] Joomla ', '').strip()
                technology = self.create_finding(
                    Technology,
                    name='Joomla',
                    version=version,
                    description=f'Joomla {version}',
                    reference='https://www.joomla.org/'
                )
            elif 'CVE : ' in data:                                              # CVE found
                aux = data.replace('CVE : ', '').strip()
                cves = [aux]
                if ',' in aux:
                    cves = aux.split(',')
                # Get name from previous line
                vulnerability_name = lines[index - 1].replace('[++]', '').replace('Joomla!', '').strip()
                for cve in cves:
                    self.create_finding(
                        Vulnerability,
                        technology=technology,                                  # Related to Joomla technology
                        name=vulnerability_name,
                        cve=cve.strip()
                    )
            elif 'EDB : ' in data:                                              # Exploit found
                link = data.replace('EDB : ', '').strip()                       # Get Exploit DB link
                self.create_finding(
                    Exploit,
                    technology=technology,                                      # Related to Joomla technology
                    title=vulnerability_name,
                    edb_id=int(link.split('https://www.exploit-db.com/exploits/', 1)[1].replace('/', '')),
                    reference=link
                )
            elif 'Debug mode Enabled' in data:
                self.create_finding(                                            # Create Vulnerability
                    Vulnerability,
                    technology=technology,                                      # Related to Joomla technology
                    name='Debug mode enabled',
                    description='Joomla debug mode enabled',
                    severity=Severity.LOW,
                    cwe='CWE-489'                                               # CWE-489: Active Debug Code
                )
            elif host in data:                                                  # Host in line, so there is an endpoint
                endpoint = data.split(host, 1)[1]                               # Get endpoint from line
                if ' ' in endpoint:
                    endpoint = endpoint.split(' ', 1)[0]                        # Remove no-endpoint data
                if endpoint and endpoint not in endpoints:                      # Check if it's a valid endpoint
                    endpoints.append(endpoint)
                    if 'Path :' in data:                                        # Endpoint with backup data
                        backups.append(endpoint)
                    if 'config file path :' in data:                            # Endpoint with configuration data
                        configurations.append(endpoint)
                    if 'Full Path Disclosure (FPD) in' in data:                 # Endpoint with path disclosure
                        path_disclosure.append(endpoint)
                    if 'directory has directory listing :' in data:             # Endpoint with directory listing
                        directory_listing.append(endpoint)
                    self.create_finding(Path, path=endpoint, type=PathType.ENDPOINT)
        for name, paths, severity, cwe in [                                     # For each vulnerability found
            # CWE-530: Exposure of Backup File to an Unauthorized Control Sphere
            ('Backup files found', backups, Severity.HIGH, 'CWE-530'),
            # CWE-497: Exposure of Sensitive System Information to an Unauthorized Control Sphere
            ('Configuration files found', configurations, Severity.MEDIUM, 'CWE-497'),
            # CWE-497: Exposure of Sensitive System Information to an Unauthorized Control Sphere
            ('Full path disclosure', path_disclosure, Severity.LOW, 'CWE-497'),
            # CWE-548: Exposure of Information Through Directory Listing
            ('Directory listing', directory_listing, Severity.LOW, 'CWE-548'),
        ]:
            if paths:
                self.create_finding(
                    Vulnerability,
                    technology=technology,                                      # Related to Joomla technology
                    name=name,
                    description=', '.join(paths),
                    severity=severity,
                    cwe=cwe
                )
