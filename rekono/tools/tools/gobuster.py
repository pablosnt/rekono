from typing import List

from findings.enums import DataType, PathType
from findings.models import OSINT, Finding, Path
from input_types.models import BaseInput

from tools.exceptions import ToolExecutionException
from tools.tools.base_tool import BaseTool


class Gobuster(BaseTool):
    '''Gobuster tool class.'''

    def get_arguments(self, targets: List[BaseInput], previous_findings: List[Finding]) -> List[str]:
        '''Get tool arguments for the tool command.

        Args:
            targets (List[BaseInput]): List of targets and resources that can be included in the tool arguments
            previous_findings (List[Finding]): List of previous findings that can be included in the tool arguments

        Raises:
            ToolExecutionException: Raised if targets and previous findings aren't enough to build the arguments

        Returns:
            List[str]: List of tool arguments to use in the tool execution
        '''
        arguments = super().get_arguments(targets, previous_findings)           # Get arguments
        if '--url' not in arguments and '--domain' not in arguments:            # URL or domain is required
            raise ToolExecutionException('Tool configuration requires url or domain argument')
        if '--wordlist' not in arguments:                                       # Wordlist is required
            raise ToolExecutionException('Tool configuration requires wordlist argument')
        return arguments

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        with open(self.path_output, 'r', encoding='utf-8') as output_file:
            data = output_file.readlines()                                      # Read output file
        for line in data:                                                       # Iterate over lines
            if ' (Status: ' in line and ') [Size: ' in line:                    # Endpoint format
                aux = line.split(' (Status: ')
                self.create_finding(
                    Path,
                    path=aux[0].strip(),
                    status=int(aux[1].split(')')[0].strip()),
                    type=PathType.ENDPOINT
                )
            elif ' Status: ' in line and ' [Size: ' in line:                    # VHOST format
                vhost, status = line.replace('Found: ', '').split(' Status: ')
                if status.split(' [')[0].strip().startswith('2'):               # Create only VHOST with status 2XX
                    if '://' in vhost:
                        vhost = vhost.split('://')[1]                           # Remove schema from VHOST URL
                    self.create_finding(
                        OSINT,
                        data=vhost.strip(),
                        data_type=DataType.VHOST,
                        source='Enumeration'
                    )
            elif ' [' in line and ']' in line:                                  # Subdomain format
                subdomain, addresses = line.replace('Found: ', '').split(' [')  # Get subdomains and IP addresses
                ips = addresses.replace(']', '').split(',')
                self.create_finding(OSINT, data=subdomain.strip(), data_type=DataType.DOMAIN, source='DNS')
                for ip in ips:
                    self.create_finding(OSINT, data=ip.strip(), data_type=DataType.IP, source='DNS')
