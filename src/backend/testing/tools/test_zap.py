from findings.enums import PathType, Severity
from findings.models import Path, Vulnerability
from testing.tools.base import ToolParserTest


class ZapParserTest(ToolParserTest):
    '''Test cases for OWASP ZAP parser.'''

    tool_name = 'ZAP'

    def test_active_scan(self) -> None:
        '''Test to parse report from active scan.'''
        expected = [
            {'model': Path, 'path': '/images/', 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/shared/', 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/shared/css/', 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/shared/images/Acunetix/', 'type': PathType.ENDPOINT},
            {
                'model': Vulnerability,
                'name': 'Directory Browsing',
                'description': (
                    'It is possible to view the directory listing.  Directory listing may reveal hidden scripts, '
                    'include files, backup source files, etc. which can be accessed to read sensitive information.\n\n'
                    'Location:\n'
                    '[GET] http://10.10.10.10/images/\n'
                    '[GET] http://10.10.10.10/shared/\n'
                    '[GET] http://10.10.10.10/shared/css/\n'
                    '[GET] http://10.10.10.10/shared/images/Acunetix/\n'
                ),
                'severity': Severity.MEDIUM,
                'cwe': 'CWE-548',
                'reference': 'http://httpd.apache.org/docs/mod/core.html#options'
            },
            {
                'model': Vulnerability,
                'name': 'X-Frame-Options Header Not Set',
                'description': (
                    'X-Frame-Options header is not included in the HTTP response to protect against '
                    "'ClickJacking' attacks.\n\n"
                    'Location:\n'
                    '[GET] http://10.10.10.10\n'
                    '[GET] http://10.10.10.10/\n'
                ),
                'severity': Severity.MEDIUM,
                'cwe': 'CWE-1021',
                'reference': 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options'
            },
            {
                'model': Vulnerability,
                'name': 'Absence of Anti-CSRF Tokens',
                'description': (
                    'No Anti-CSRF tokens were found in a HTML submission form.A cross-site request forgery '
                    'is an attack that involves forcing a victim to send an HTTP request to a target destination '
                    'without their knowledge or intent in order to perform an action as the victim. The underlying '
                    'cause is application functionality using predictable URL/form actions in a repeatable way. '
                    'The nature of the attack is that CSRF exploits the trust that a web site has for a user. '
                    'By contrast, cross-site scripting (XSS) exploits the trust that a user has for a web site. '
                    'Like XSS, CSRF attacks are not necessarily cross-site, but they can be. Cross-site request '
                    'forgery is also known as CSRF, XSRF, one-click attack, session riding, confused deputy, and '
                    'sea surf.CSRF attacks are effective in a number of situations, including:    * The victim '
                    'has an active session on the target site.    * The victim is authenticated via HTTP auth on '
                    'the target site.    * The victim is on the same local network as the target site.CSRF has '
                    "primarily been used to perform an action against a target site using the victim's privileges, "
                    'but recent techniques have been discovered to disclose information by gaining access to the '
                    'response. The risk of information disclosure is dramatically increased when the target site '
                    'is vulnerable to XSS, because XSS can be used as a platform for CSRF, allowing the attack to '
                    'operate within the bounds of the same-origin policy.\n\n'
                    'Location:\n'
                    '[GET] http://10.10.10.10\n'
                    '[GET] http://10.10.10.10/\n'
                ),
                'severity': Severity.LOW,
                'cwe': 'CWE-352',
                'reference': 'http://projects.webappsec.org/Cross-Site-Request-Forgery'
            },
            {
                'model': Vulnerability,
                'name': 'Cross-Domain JavaScript Source File Inclusion',
                'description': (
                    'The page includes one or more script files from a third-party domain.\n\n'
                    'Location:\n'
                    '[GET] http://10.10.10.10\n'
                    '[GET] http://10.10.10.10\n'
                    '[GET] http://10.10.10.10/\n'
                    '[GET] http://10.10.10.10/\n'
                ),
                'severity': Severity.LOW,
                'cwe': 'CWE-829'
            },
            {
                'model': Path,
                'path': '/shared/images/Acunetix/acx_Chess-WB.gif',
                'type': PathType.ENDPOINT
            },
            {
                'model': Vulnerability,
                'name': 'Timestamp Disclosure - Unix',
                'description': (
                    'A timestamp was disclosed by the application/web server - Unix\n\n'
                    'Location:\n'
                    '[GET] http://10.10.10.10\n'
                    '[GET] http://10.10.10.10/\n'
                    '[GET] http://10.10.10.10/shared/images/Acunetix/acx_Chess-WB.gif\n'
                ),
                'severity': Severity.LOW,
                'cwe': 'CWE-200',
                'reference': 'http://projects.webappsec.org/w/page/13246936/Information%20Leakage'
            },
            {'model': Path, 'path': '/images/sitelogo.png', 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/shared/css/insecdb.css', 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/shared/images/tiny-eyeicon.png', 'type': PathType.ENDPOINT},
            {'model': Path, 'path': '/shared/images/topleftcurve.gif', 'type': PathType.ENDPOINT},
            {
                'model': Vulnerability,
                'name': 'X-Content-Type-Options Header Missing',
                'description': (
                    "The Anti-MIME-Sniffing header X-Content-Type-Options was not set to 'nosniff'. "
                    'This allows older versions of Internet Explorer and Chrome to perform MIME-sniffing '
                    'on the response body, potentially causing the response body to be interpreted and '
                    'displayed as a content type other than the declared content type. Current (early 2014) '
                    'and legacy versions of Firefox will use the declared content type (if one is set), '
                    'rather than performing MIME-sniffing.\n\n'
                    'Location:\n'
                    '[GET] http://10.10.10.10\n'
                    '[GET] http://10.10.10.10/\n'
                    '[GET] http://10.10.10.10/images/sitelogo.png\n'
                    '[GET] http://10.10.10.10/shared/css/insecdb.css\n'
                    '[GET] http://10.10.10.10/shared/images/Acunetix/acx_Chess-WB.gif\n'
                    '[GET] http://10.10.10.10/shared/images/tiny-eyeicon.png\n'
                    '[GET] http://10.10.10.10/shared/images/topleftcurve.gif\n'
                ),
                'severity': Severity.LOW,
                'cwe': 'CWE-693',
                'reference': 'http://msdn.microsoft.com/en-us/library/ie/gg622941%28v=vs.85%29.aspx'
            }
        ]
        super().check_tool_file_parser('active-scan.xml', expected)
