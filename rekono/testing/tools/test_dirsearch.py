from findings.enums import EndpointProtocol
from findings.models import Endpoint
from testing.tools.base import ToolParserTest


class DirsearchParserTest(ToolParserTest):
    '''Test cases for Dirsearch parser.'''

    tool_name = 'Dirsearch'

    def test_default(self) -> None:
        '''Test to parse generic report.'''
        expected = [
            {'model': Endpoint, 'endpoint': '/.ht_wsr.txt', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htaccess.sample', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htaccess_orig', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htaccess.bak1', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htaccess_sc', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htaccess.save', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htaccess.orig', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htaccess_extra', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htm', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htaccessBAK', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.httr-oauth', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htaccessOLD2', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.html', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htaccessOLD', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htpasswds', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.htpasswd_test', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/.php', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/assets/', 'status': 200, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/assets', 'status': 301, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/index.html', 'status': 200, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/server-status', 'status': 403, 'protocol': EndpointProtocol.HTTP},
            {'model': Endpoint, 'endpoint': '/server-status/', 'status': 403, 'protocol': EndpointProtocol.HTTP},
        ]
        super().check_tool_file_parser('default.json', expected)
