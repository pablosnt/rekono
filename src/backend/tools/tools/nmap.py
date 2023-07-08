import re
from typing import Any, Callable, Dict, List, Tuple, Union, cast

from django.db.models import TextChoices
from findings.enums import OSType, PathType, PortStatus, Protocol, Severity
from findings.models import (Credential, Host, Path, Port, Technology,
                             Vulnerability)
from libnmap.parser import NmapParser
from security.input_validation import CVE_REGEX
from tools.tools.base_tool import BaseTool


class Nmap(BaseTool):
    '''Nmap tool class.'''

    def get_smb_technology(self, technologies: Dict[str, Technology]) -> Union[Technology, None]:
        '''Get Technology related to SMB protocol.

        Args:
            technologies (Dict[str, Technology]): Technologies found in this host

        Returns:
            Union[Technology, None]: Technology related to SMB service if found
        '''
        if 'microsoft-ds' in technologies:
            return technologies['microsoft-ds']
        return None

    def parse_vulners_nse(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Create Vulnerabilities with CVE reported by NSE script vulners.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        created = set()
        cves: List[str] = re.findall(CVE_REGEX, script.get('output', ''))       # Search CVE patterns in vulners output
        for cve in cves:                                                        # For each CVE
            if cve not in created:                                              # Check if CVE has been used before
                created.add(cve)
                # Create Vulnerability
                self.create_finding(Vulnerability, technology=technology, name=cve, cve=cve)

    def create_ftp_anonymous(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Create FTP anonymous Vulnerability reported by NSE script ftp-anon.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='Anonymous FTP',
            description='Anonymous login is allowed in FTP',
            severity=Severity.CRITICAL,
            cwe='CWE-287',                                                      # CWE-287: Improper Authentication
            reference='https://book.hacktricks.xyz/pentesting/pentesting-ftp#anonymous-login'
        )

    def create_ftp_proftpd_backdoor(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Create backdoor Vulnerability reported by NSE script ftp-proftpd-backdoor.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='FTP Backdoor',
            description='FTP ProFTPD 1.3.3c Backdoor',
            severity=Severity.CRITICAL,
            # CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
            cwe='CWE-78',
            osvdb='OSVDB-69562'
        )

    def create_cve_2011_2523(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Create Vulnerability CVE-2011-2523 reported by NSE script ftp-vsftpd-backdoor.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        self.create_finding(Vulnerability, technology=technology, name='vsFTPd Backdoor', cve='CVE-2011-2523')

    def create_cve_2010_1938(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Create Vulnerability CVE-2010-1938 reported by NSE script ftp-libopie.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='OPIE off-by-one stack overflow',
            cve='CVE-2010-1938'
        )

    def create_cve_2010_4221(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Create Vulnerability CVE-2010-4221 reported by NSE script ftp-vuln-cve2010-4221.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='ProFTPD server TELNET IAC stack overflow',
            cve='CVE-2010-4221'
        )

    def create_cve_2017_7494(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Create Vulnerability CVE-2017-7494 reported by NSE script smb-vuln-cve-2017-7494.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='SAMBA Remote Code Execution from Writable Share',
            cve='CVE-2017-7494'
        )

    def create_cve_2018_15442(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Create Vulnerability CVE-2018-15442 reported by NSE script smb-vuln-webexec.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='Remote Code Execution vulnerability in WebExService',
            cve='CVE-2018-15442'
        )

    def create_smb_double_pulsar_backdoor(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Create backdoor Vulnerability reported by NSE script smb-double-pulsar-backdoor.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='SMB Server DOUBLEPULSAR Backdoor',
            description=(
                'NNM detected the presence of DOUBLEPULSAR on the remote Windows host. DOUBLEPULSAR is one of '
                'multiple Equation Group SMB implants and backdoors disclosed on 2017/04/14 by a group known as '
                "the 'Shadow Brokers'. The implant allows an unauthenticated, remote attacker to use SMB as a "
                'covert channel to exfiltrate data, launch remote commands, or execute arbitrary code.'
            ),
            severity=Severity.CRITICAL,
            # CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
            cwe='CWE-78',
            reference='https://www.tenable.com/plugins/nnm/700059'
        )

    def parse_smb_shares(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Parse findings reported by NSE script smb-enum-shares.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        for share, fields in script.get('elements', {}).items():
            if 'account_used' not in share:
                path = share
                if '\\' in path:
                    path = path.rsplit('\\', 1)[1]                              # Remove host information
                anonymous = fields.get("Anonymous access")
                self.create_finding(                                            # Create share finding
                    Path,
                    port=technology.port if technology else None,
                    path=path,
                    extra=(
                        f'{fields.get("Comment") or ""} '
                        f'Type: {fields.get("Type")} '
                        f'Anonymous access: {anonymous} '
                        f'Current access: {fields.get("Current user access")}'
                    ).strip(),
                    type=PathType.SHARE
                )
                if 'READ' in anonymous or 'WRITE' in anonymous:
                    self.create_finding(
                        Vulnerability,
                        technology=technology,
                        name='Anonymous SMB',
                        description=f'Anonymous access is allowed to the SMB share {path}',
                        severity=Severity.CRITICAL if 'WRITE' in anonymous else Severity.HIGH,
                        cwe='CWE-287'                                           # CWE-287: Improper Authentication
                    )

    def parse_smb_users(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Parse findings reported by NSE script smb-enum-users.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        for line in script.get('output').split('\n'):
            data = line.strip()
            if data and ' (RID:' in data:
                self.create_finding(
                    Credential,
                    technology=technology,
                    username=data.split(' (RID:', 1)[0],
                    context='SMB user'
                )

    def parse_smb_protocols(self, script: Any, technology: Union[Technology, None]) -> None:
        '''Parse findings reported by NSE script smb-enum-shares.

        Args:
            script (Any): NSE script output
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
        '''
        if technology:
            protocols = []
            for protocol in script.get('elements', {}).get('dialects', {}).get(None):
                protocols.append(
                    protocol if '[dangerous' not in protocol else protocol.split('[dangerous', 1)[0].strip()
                )
            technology.description = f'Protocols: {", ".join(protocols)}'
            technology.save(update_fields=['description'])

    def parse_nse_scripts(
        self,
        scripts_results: Any,
        technology: Union[Technology, None],
        technologies: Dict[str, Technology]
    ) -> None:
        '''Parse NSE scripts reports.

        Args:
            scripts_results (Any): NSE scripts reports obtained from nmap parser
            technology (Union[Technology, None]): Technology associated to the NSE scripts execution
            technologies (Dict[str, Technology]): Technologies found in this host. Only used when technology is None
        '''
        smb_technology = technology if technology else self.get_smb_technology(technologies)        # Get SMB technology
        # Mapping between NSE script names and parsers
        parsers: Dict[str, Tuple[Callable, Union[Technology, None]]] = {
            'vulners': (self.parse_vulners_nse, technology),
            'ftp-anon': (self.create_ftp_anonymous, technology),
            'ftp-proftpd-backdoor': (self.create_ftp_proftpd_backdoor, technology),
            'ftp-vsftpd-backdoor': (self.create_cve_2011_2523, technology),
            'ftp-libopie': (self.create_cve_2010_1938, technology),
            'ftp-vuln-cve2010-4221': (self.create_cve_2010_4221, technology),
            'smb-double-pulsar-backdoor': (self.create_smb_double_pulsar_backdoor, smb_technology),
            'smb-vuln-webexec': (self.create_cve_2018_15442, smb_technology),
            'smb-vuln-cve-2017-7494': (self.create_cve_2017_7494, smb_technology),
            'smb2-vuln-uptime': (self.parse_vulners_nse, smb_technology),
            'smb-vuln-ms06-025': (self.parse_vulners_nse, smb_technology),
            'smb-vuln-ms07-029': (self.parse_vulners_nse, smb_technology),
            'smb-vuln-ms10-061': (self.parse_vulners_nse, smb_technology),
            'smb-vuln-ms17-010': (self.parse_vulners_nse, smb_technology),
            'smb-enum-users': (self.parse_smb_users, smb_technology),
            'smb-enum-shares': (self.parse_smb_shares, smb_technology),
            'smb-protocols': (self.parse_smb_protocols, smb_technology),
        }
        for script in scripts_results:                                          # For each NSE script
            if script.get('id') in parsers:                                     # Script Id found
                parser, tech = parsers[script.get('id')]
                parser(script, tech)                                            # Process NSE result
            else:
                self.parse_vulners_nse(script, technology)                      # By default, search CVEs

    def select_os_detection(self, os_detection: Any) -> Tuple[str, OSType]:
        '''Select OS detection based on its accuracy.

        Args:
            os_detection (Any): OS detection obtained from nmap parser

        Returns:
            Tuple[str, OSType]: Selected OS detection text and type
        '''
        os_text = ''                                                            # Initialize selection
        os_type = OSType.OTHER
        if os_detection:                                                        # If OS detection exists
            selected_os = None                                                  # Initialize selected OS and accuracy
            accuracy = 0
            for o in os_detection:                                              # For each OS detection
                # If his accuracy is greater than the selected one
                if o.accuracy > accuracy:
                    selected_os = o                                             # Select OS detection
                    os_text = o.name                                            # Save OS name
                    accuracy = o.accuracy                                       # Update selected accuracy
            if selected_os:
                accuracy = 0                                                    # Reset accuracy to 0
                for c in selected_os.osclasses:                                 # For each OS class
                    # If his accuracy is greater than the selected one
                    if c.accuracy > accuracy:
                        try:
                            os_type = cast(TextChoices, OSType)[c.osfamily.upper()]     # Get OS type based on OS family
                        except KeyError:
                            os_type = OSType.OTHER                              # By default, get OTHER OS type
                        accuracy = o.accuracy                                   # Update selected accuracy
        return os_text, cast(OSType, os_type)

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        report = NmapParser.parse_fromfile(self.path_output)                    # Parse nmap report
        for h in report.hosts:                                                  # For each host
            if not h.is_up():                                                   # Host is down
                continue
            # Get OS information based on OS detection accuracy
            os_text, os_type = self.select_os_detection(h.os_match_probabilities())
            host = self.create_finding(Host, address=h.address, os=os_text, os_type=os_type)    # Create host
            technology = None
            technologies = {}
            for s in h.services:                                                # For each service
                port = self.create_finding(                                     # Create Port
                    Port,
                    host=host,
                    port=s.port,
                    status=cast(TextChoices, PortStatus)[s.state.upper()],
                    protocol=cast(TextChoices, Protocol)[s.protocol.upper()],
                    service=s.service
                )
                if 'product' in s.service_dict and 'version' in s.service_dict:     # If service details found
                    technology = self.create_finding(                           # Create technology
                        Technology,
                        port=port,
                        name=s.service_dict['product'],
                        version=s.service_dict['version']
                    )
                    technologies[s.service] = technology
                    if s.scripts_results:                                       # If results from NSE scripts found
                        # Parse NSE scripts results
                        self.parse_nse_scripts(s.scripts_results, technology, technologies)
            if h.scripts_results:
                self.parse_nse_scripts(h.scripts_results, technology if len(h.services) == 1 else None, technologies)
