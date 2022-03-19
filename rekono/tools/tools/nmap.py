import re
from typing import Any, List, Tuple, cast

from django.db.models import TextChoices
from findings.enums import OSType, PortStatus, Protocol, Severity
from findings.models import Enumeration, Host, Technology, Vulnerability
from libnmap.parser import NmapParser
from tools.tools.base_tool import BaseTool

# CVE regex
CVE_REGEX = 'CVE-[0-9]{4}-[0-9]{1,7}'


class NmapTool(BaseTool):
    '''Nmap tool class.'''

    def parse_vulners_nse(self, technology: Technology, output: str = None) -> None:
        '''Create Vulnerabilities with CVE reported by NSE script vulners.

        Args:
            technology (Technology): Technology associated to the NSE scripts execution
            output (str, optional): NSE script vulners output
        '''
        if output:
            created = set()
            cves: List[str] = re.findall(CVE_REGEX, output)                     # Search CVE patterns in vulners output
            for cve in cves:                                                    # For each CVE
                if cve not in created:                                          # Check if CVE has been used before
                    created.add(cve)
                    # Create Vulnerability
                    self.create_finding(Vulnerability, technology=technology, name=cve, cve=cve)

    def create_ftp_anonymous(self, technology: Technology, output: str = None) -> None:
        '''Create FTP anonymous Vulnerability reported by NSE script ftp-anon.

        Args:
            technology (Technology): Technology associated to the NSE scripts execution
            output (str, optional): Not used. Defaults to None.
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

    def create_ftp_proftpd_backdoor(self, technology: Technology, output: str = None) -> None:
        '''Create backdoor Vulnerability reported by NSE script ftp-proftpd-backdoor.

        Args:
            technology (Technology): Technology associated to the NSE scripts execution
            output (str, optional): Not used. Defaults to None.
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

    def create_cve_2011_2523(self, technology: Technology, output: str = None) -> None:
        '''Create Vulnerability CVE-2011-2523 reported by NSE script ftp-vsftpd-backdoor.

        Args:
            technology (Technology): Technology associated to the NSE scripts execution
            output (str, optional): Not used. Defaults to None.
        '''
        self.create_finding(Vulnerability, technology=technology, name='vsFTPd Backdoor', cve='CVE-2011-2523')

    def create_cve_2010_1938(self, technology: Technology, output: str = None) -> None:
        '''Create Vulnerability CVE-2010-1938 reported by NSE script ftp-libopie.

        Args:
            technology (Technology): Technology associated to the NSE scripts execution
            output (str, optional): Not used. Defaults to None.
        '''
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='OPIE off-by-one stack overflow',
            cve='CVE-2010-1938'
        )

    def create_cve_2010_4221(self, technology: Technology, output: str = None) -> None:
        '''Create Vulnerability CVE-2010-4221 reported by NSE script ftp-vuln-cve2010-4221.

        Args:
            technology (Technology): Technology associated to the NSE scripts execution
            output (str, optional): Not used. Defaults to None.
        '''
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='ProFTPD server TELNET IAC stack overflow',
            cve='CVE-2010-4221'
        )

    def create_cve_2017_7494(self, technology: Technology, output: str = None) -> None:
        '''Create Vulnerability CVE-2017-7494 reported by NSE script smb-vuln-cve-2017-7494.

        Args:
            technology (Technology): Technology associated to the NSE scripts execution
            output (str, optional): Not used. Defaults to None.
        '''
        self.create_finding(
            Vulnerability,
            name='SAMBA Remote Code Execution from Writable Share',
            cve='CVE-2017-7494'
        )

    def create_cve_2018_15442(self, technology: Technology, output: str = None) -> None:
        '''Create Vulnerability CVE-2018-15442 reported by NSE script smb-vuln-webexec.

        Args:
            technology (Technology): Technology associated to the NSE scripts execution
            output (str, optional): Not used. Defaults to None.
        '''
        self.create_finding(
            Vulnerability,
            name='Remote Code Execution vulnerability in WebExService',
            cve='CVE-2018-15442'
        )

    def create_smb_double_pulsar_backdoor(self, technology: Technology, output: str = None) -> None:
        '''Create backdoor Vulnerability reported by NSE script smb-double-pulsar-backdoor.

        Args:
            technology (Technology): Technology associated to the NSE scripts execution
            output (str, optional): Not used. Defaults to None.
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

    def parse_nse_scripts(self, scripts_results: Any, technology: Technology) -> None:
        '''Parse NSE scripts reports.

        Args:
            scripts_results (Any): NSE scripts reports obtained from nmap parser
            technology (Technology): Technology associated to the NSE scripts execution
        '''
        # Mapping between NSE script names and methods to process its result
        callbacks = {
            'vulners': self.parse_vulners_nse,
            'ftp-anon': self.create_ftp_anonymous,
            'ftp-proftpd-backdoor': self.create_ftp_proftpd_backdoor,
            'ftp-vsftpd-backdoor': self.create_cve_2011_2523,
            'ftp-libopie': self.create_cve_2010_1938,
            'ftp-vuln-cve2010-4221': self.create_cve_2010_4221,
            'smb-double-pulsar-backdoor': self.create_smb_double_pulsar_backdoor,
            'smb-vuln-webexec': self.create_cve_2018_15442,
            'smb2-vuln-uptime': self.parse_vulners_nse,
            'smb-vuln-ms06-025': self.parse_vulners_nse,
            'smb-vuln-ms07-029': self.parse_vulners_nse,
            'smb-vuln-ms10-061': self.parse_vulners_nse,
            'smb-vuln-ms17-010': self.parse_vulners_nse,
            'smb-vuln-cve-2017-7494': self.create_cve_2017_7494,
        }
        for script in scripts_results:                                          # For each NSE script
            if script.get('id') not in callbacks:                               # NSE Id not found
                continue
            callbacks[script.get('id')](technology, script.get('output'))       # Process NSE result

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
            for s in h.services:                                                # For each service
                enumeration = self.create_finding(                              # Create Enumeration
                    Enumeration,
                    host=host,
                    port=s.port,
                    port_status=cast(TextChoices, PortStatus)[s.state.upper()],
                    protocol=cast(TextChoices, Protocol)[s.protocol.upper()],
                    service=s.service
                )
                if 'product' in s.service_dict and 'version' in s.service_dict:     # If service details found
                    technology = self.create_finding(                           # Create technology
                        Technology,
                        enumeration=enumeration,
                        name=s.service_dict['product'],
                        version=s.service_dict['version']
                    )
                    if s.scripts_results:                                       # If results from NSE scripts found
                        self.parse_nse_scripts(s.scripts_results, technology)   # Parse NSE scripts results
