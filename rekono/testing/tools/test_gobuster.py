from findings.enums import DataType, PathType
from findings.models import OSINT, Path
from testing.tools.base import ToolParserTest


class GobusterParserTest(ToolParserTest):
    '''Test cases for Gobuster parser.'''

    tool_name = 'Gobuster'

    def test_dir(self) -> None:
        '''Test to parse dir report with endpoints.'''
        expected = [
            {'model': Path, 'path': '/.gitignore', 'status': 200, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/.hta', 'status': 403, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/.htaccess', 'status': 403, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/.htpasswd', 'status': 403, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/config', 'status': 301, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/docs', 'status': 301, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/external', 'status': 301, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/favicon.ico', 'status': 200, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/index.php', 'status': 302, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/php.ini', 'status': 200, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/phpinfo.php', 'status': 302, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/robots.txt', 'status': 200, 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/server-status', 'status': 403, 'type': PathType.ENDPOINT},
        ]
        super().check_tool_file_parser('dir.txt', expected)

    def test_dns(self) -> None:
        '''Test to parse dns report with domains and IPs.'''
        expected = [
            {
                'model': OSINT,
                'data': 'chat.example.com',
                'data_type': DataType.DOMAIN,
                'source': 'DNS'
            },
            {'model': OSINT, 'data': '10.10.10.10', 'data_type': DataType.IP, 'source': 'DNS'},
            {'model': OSINT, 'data': '10.10.10.11', 'data_type': DataType.IP, 'source': 'DNS'},
            {
                'model': OSINT,
                'data': 'echo.example.com',
                'data_type': DataType.DOMAIN,
                'source': 'DNS'
            },
            {'model': OSINT, 'data': '10.10.10.10', 'data_type': DataType.IP, 'source': 'DNS'},
            {'model': OSINT, 'data': '10.10.10.11', 'data_type': DataType.IP, 'source': 'DNS'},
        ]
        super().check_tool_file_parser('dns.txt', expected)

    def test_vhost(self) -> None:
        '''Test to parse vhost report with VHOSTs.'''
        expected = [
            {
                'model': OSINT,
                'data': 'enquetes.example.com',
                'data_type': DataType.VHOST,
                'source': 'Enumeration'
            }
        ]
        super().check_tool_file_parser('vhost.txt', expected)
