from findings.enums import DataType
from findings.models import OSINT
from testing.tools.base import ToolParserTest


class TheHarvesterParserTest(ToolParserTest):
    '''Test cases for theHarvester parser.'''

    tool_name = 'theHarvester'

    def test_nmap_dot_org(self) -> None:
        '''Test to parse report from scanme.nmap.org.'''
        expected = [
            {'model': OSINT, 'data': '45.33.32.156', 'data_type': DataType.IP},
            {'model': OSINT, 'data': '74.207.244.221', 'data_type': DataType.IP},
            {'model': OSINT, 'data': '2600:3c01::f03c:91ff:fe18:bb2f', 'data_type': DataType.IP},
            {'model': OSINT, 'data': 'http://scanme.nmap.org', 'data_type': DataType.URL},
            {'model': OSINT, 'data': 'http://scanme.nmap.org/', 'data_type': DataType.URL},
            {'model': OSINT, 'data': 'http://scanme.nmap.org//r/n/r/nUser:/r/n-', 'data_type': DataType.URL},
            {'model': OSINT, 'data': 'AS63949', 'data_type': DataType.ASN},
        ]
        super().check_tool_file_parser('scanme.json', expected)
