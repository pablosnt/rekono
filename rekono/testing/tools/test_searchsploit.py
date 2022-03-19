from findings.models import Exploit
from testing.tools.base import ToolParserTest


class SearchSploitParserTest(ToolParserTest):
    '''Test cases for SearchSploit parser.'''

    tool_name = 'SearchSploit'

    def test_searchsploit_with_exploits(self) -> None:
        '''Test to parse report with exploits.'''
        expected = [
            {
                'model': Exploit,
                'title': "WordPress Core 1.2.1/1.2.2 - '/wp-admin/post.php?content' Cross-Site Scripting",
                'edb_id': 24988,
                'reference': 'https://www.exploit-db.com/exploits/24988'
            },
            {
                'model': Exploit,
                'title': "WordPress Core 1.2.1/1.2.2 - '/wp-admin/templates.php?file' Cross-Site Scripting",
                'edb_id': 24989,
                'reference': 'https://www.exploit-db.com/exploits/24989'
            },
            {
                'model': Exploit,
                'title': "WordPress Core 1.2.1/1.2.2 - 'link-add.php' Multiple Cross-Site Scripting Vulnerabilities",
                'edb_id': 24990,
                'reference': 'https://www.exploit-db.com/exploits/24990'
            },
            {
                'model': Exploit,
                'title': "WordPress Core 1.2.1/1.2.2 - 'link-categories.php?cat_id' Cross-Site Scripting",
                'edb_id': 24991,
                'reference': 'https://www.exploit-db.com/exploits/24991'
            },
            {
                'model': Exploit,
                'title': (
                    "WordPress Core 1.2.1/1.2.2 - 'link-manager.php' Multiple Cross-Site Scripting Vulnerabilities"
                ),
                'edb_id': 24992,
                'reference': 'https://www.exploit-db.com/exploits/24992'
            },
            {
                'model': Exploit,
                'title': "WordPress Core 1.2.1/1.2.2 - 'moderation.php?item_approved' Cross-Site Scripting",
                'edb_id': 24993,
                'reference': 'https://www.exploit-db.com/exploits/24993'
            },
            {
                'model': Exploit,
                'title': 'WordPress Core 1.5.1.1 < 2.2.2 - Multiple Vulnerabilities',
                'edb_id': 4397,
                'reference': 'https://www.exploit-db.com/exploits/4397'
            },
            {
                'model': Exploit,
                'title': "WordPress Core 2.0 < 2.7.1 - 'admin.php' Module Configuration Security Bypass",
                'edb_id': 10088,
                'reference': 'https://www.exploit-db.com/exploits/10088'
            },
            {
                'model': Exploit,
                'title': "WordPress Core 2.1.1 - '/wp-includes/theme.php?iz' Arbitrary Command Execution",
                'edb_id': 29702,
                'reference': 'https://www.exploit-db.com/exploits/29702'
            },
            {
                'model': Exploit,
                'title': "WordPress Core 2.1.1 - 'post.php' Cross-Site Scripting",
                'edb_id': 29682,
                'reference': 'https://www.exploit-db.com/exploits/29682'
            },
            {
                'model': Exploit,
                'title': 'WordPress Core 2.1.1 - Arbitrary Command Execution',
                'edb_id': 29701,
                'reference': 'https://www.exploit-db.com/exploits/29701'
            },
            {
                'model': Exploit,
                'title': 'WordPress Core 2.1.1 - Multiple Cross-Site Scripting Vulnerabilities',
                'edb_id': 29684,
                'reference': 'https://www.exploit-db.com/exploits/29684'
            },
            {
                'model': Exploit,
                'title': "WordPress Core 2.1.2 - 'xmlrpc' SQL Injection",
                'edb_id': 3656,
                'reference': 'https://www.exploit-db.com/exploits/3656'
            },
            {
                'model': Exploit,
                'title': "WordPress Core 2.1.3 - 'admin-ajax.php' SQL Injection Blind Fishing",
                'edb_id': 3960,
                'reference': 'https://www.exploit-db.com/exploits/3960'
            },
            {
                'model': Exploit,
                'title': "WordPress Core < 2.1.2 - 'PHP_Self' Cross-Site Scripting",
                'edb_id': 29754,
                'reference': 'https://www.exploit-db.com/exploits/29754'
            },
            {
                'model': Exploit,
                'title': 'WordPress Core < 2.8.5 - Unrestricted Arbitrary File Upload / Arbitrary PHP Code Execution',
                'edb_id': 10089,
                'reference': 'https://www.exploit-db.com/exploits/10089'
            },
            {
                'model': Exploit,
                'title': 'WordPress Core < 4.0.1 - Denial of Service',
                'edb_id': 35414,
                'reference': 'https://www.exploit-db.com/exploits/35414'
            },
            {
                'model': Exploit,
                'title': 'WordPress Core < 4.7.1 - Username Enumeration',
                'edb_id': 41497,
                'reference': 'https://www.exploit-db.com/exploits/41497'
            },
            {
                'model': Exploit,
                'title': 'WordPress Core < 4.7.4 - Unauthorized Password Reset',
                'edb_id': 41963,
                'reference': 'https://www.exploit-db.com/exploits/41963'
            },
            {
                'model': Exploit,
                'title': 'WordPress Core < 4.9.6 - (Authenticated) Arbitrary File Deletion',
                'edb_id': 44949,
                'reference': 'https://www.exploit-db.com/exploits/44949'
            },
            {
                'model': Exploit,
                'title': 'WordPress Core < 5.2.3 - Viewing Unauthenticated/Password/Private Posts',
                'edb_id': 47690,
                'reference': 'https://www.exploit-db.com/exploits/47690'
            },
            {
                'model': Exploit,
                'title': "WordPress Core < 5.3.x - 'xmlrpc.php' Denial of Service",
                'edb_id': 47800,
                'reference': 'https://www.exploit-db.com/exploits/47800'
            }
        ]
        super().check_tool_file_parser('exploits.json', expected)

    def test_searchsploit_without_exploits(self) -> None:
        '''Test to parse an empty report.'''
        super().check_tool_file_parser('nothing.json', [])
