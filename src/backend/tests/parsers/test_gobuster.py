from findings.enums import OSINTDataType, PathType
from findings.models import OSINT, Path
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class GobusterTest(ToolTest):
    tool_name = "Gobuster"
    cases = [
        ToolTestCase(
            "dir.txt",
            [
                {
                    "model": Path,
                    "path": "/.gitignore",
                    "status": 200,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/.hta",
                    "status": 403,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/.htaccess",
                    "status": 403,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/.htpasswd",
                    "status": 403,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/config",
                    "status": 301,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/docs",
                    "status": 301,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/external",
                    "status": 301,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/favicon.ico",
                    "status": 200,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/index.php",
                    "status": 302,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/php.ini",
                    "status": 200,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/phpinfo.php",
                    "status": 302,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/robots.txt",
                    "status": 200,
                    "type": PathType.ENDPOINT,
                },
                {
                    "model": Path,
                    "path": "/server-status",
                    "status": 403,
                    "type": PathType.ENDPOINT,
                },
            ],
        ),
        ToolTestCase(
            "dns.txt",
            [
                {
                    "model": OSINT,
                    "data": "chat.example.com",
                    "data_type": OSINTDataType.DOMAIN,
                    "source": "DNS",
                },
                {
                    "model": OSINT,
                    "data": "10.10.10.10",
                    "data_type": OSINTDataType.IP,
                    "source": "DNS",
                },
                {
                    "model": OSINT,
                    "data": "10.10.10.11",
                    "data_type": OSINTDataType.IP,
                    "source": "DNS",
                },
                {
                    "model": OSINT,
                    "data": "echo.example.com",
                    "data_type": OSINTDataType.DOMAIN,
                    "source": "DNS",
                },
                {
                    "model": OSINT,
                    "data": "10.10.10.10",
                    "data_type": OSINTDataType.IP,
                    "source": "DNS",
                },
                {
                    "model": OSINT,
                    "data": "10.10.10.11",
                    "data_type": OSINTDataType.IP,
                    "source": "DNS",
                },
            ],
        ),
        ToolTestCase(
            "vhost.txt",
            [
                {
                    "model": OSINT,
                    "data": "enquetes.example.com",
                    "data_type": OSINTDataType.VHOST,
                    "source": "Enumeration",
                }
            ],
        ),
    ]
