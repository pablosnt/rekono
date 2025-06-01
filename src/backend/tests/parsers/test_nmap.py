from findings.enums import HostOS, PathType, PortStatus, Protocol, Severity
from findings.models import Credential, Host, Path, Port, Technology, Vulnerability
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class NmapTest(ToolTest):
    tool_name = "Nmap"
    cases = [
        ToolTestCase(
            "enumeration-vulners.xml",
            [
                {
                    "model": Host,
                    "ip": "10.10.10.10",
                    "os": "Linux 3.2 - 4.9",
                    "os_type": HostOS.LINUX,
                },
                {
                    "model": Port,
                    "port": 22,
                    "status": PortStatus.OPEN,
                    "protocol": Protocol.TCP,
                    "service": "ssh",
                },
                {"model": Technology, "name": "OpenSSH", "version": "8.0"},
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-15778",
                    "cve": "CVE-2020-15778",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-41617",
                    "cve": "CVE-2021-41617",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-16905",
                    "cve": "CVE-2019-16905",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-14145",
                    "cve": "CVE-2020-14145",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2016-20012",
                    "cve": "CVE-2016-20012",
                },
                {
                    "model": Port,
                    "port": 80,
                    "status": PortStatus.OPEN,
                    "protocol": Protocol.TCP,
                    "service": "http",
                },
                {"model": Technology, "name": "Apache httpd", "version": "2.4.37"},
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-11984",
                    "cve": "CVE-2020-11984",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-44790",
                    "cve": "CVE-2021-44790",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-39275",
                    "cve": "CVE-2021-39275",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-26691",
                    "cve": "CVE-2021-26691",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0211",
                    "cve": "CVE-2019-0211",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-40438",
                    "cve": "CVE-2021-40438",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-35452",
                    "cve": "CVE-2020-35452",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-44224",
                    "cve": "CVE-2021-44224",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-10082",
                    "cve": "CVE-2019-10082",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0217",
                    "cve": "CVE-2019-0217",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0215",
                    "cve": "CVE-2019-0215",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-10097",
                    "cve": "CVE-2019-10097",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-1927",
                    "cve": "CVE-2020-1927",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-10098",
                    "cve": "CVE-2019-10098",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-9490",
                    "cve": "CVE-2020-9490",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-1934",
                    "cve": "CVE-2020-1934",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-36160",
                    "cve": "CVE-2021-36160",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-34798",
                    "cve": "CVE-2021-34798",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-33193",
                    "cve": "CVE-2021-33193",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-26690",
                    "cve": "CVE-2021-26690",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-17567",
                    "cve": "CVE-2019-17567",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-10081",
                    "cve": "CVE-2019-10081",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0220",
                    "cve": "CVE-2019-0220",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0196",
                    "cve": "CVE-2019-0196",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2018-17199",
                    "cve": "CVE-2018-17199",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2018-17189",
                    "cve": "CVE-2018-17189",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0197",
                    "cve": "CVE-2019-0197",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-11993",
                    "cve": "CVE-2020-11993",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-10092",
                    "cve": "CVE-2019-10092",
                },
                {
                    "model": Port,
                    "port": 443,
                    "status": PortStatus.OPEN,
                    "protocol": Protocol.TCP,
                    "service": "http",
                },
                {"model": Technology, "name": "Apache httpd", "version": "2.4.37"},
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-11984",
                    "cve": "CVE-2020-11984",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-44790",
                    "cve": "CVE-2021-44790",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-39275",
                    "cve": "CVE-2021-39275",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-26691",
                    "cve": "CVE-2021-26691",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0211",
                    "cve": "CVE-2019-0211",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-40438",
                    "cve": "CVE-2021-40438",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-35452",
                    "cve": "CVE-2020-35452",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-44224",
                    "cve": "CVE-2021-44224",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-10082",
                    "cve": "CVE-2019-10082",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0217",
                    "cve": "CVE-2019-0217",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0215",
                    "cve": "CVE-2019-0215",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-10097",
                    "cve": "CVE-2019-10097",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-1927",
                    "cve": "CVE-2020-1927",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-10098",
                    "cve": "CVE-2019-10098",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-9490",
                    "cve": "CVE-2020-9490",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-1934",
                    "cve": "CVE-2020-1934",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-36160",
                    "cve": "CVE-2021-36160",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-34798",
                    "cve": "CVE-2021-34798",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-33193",
                    "cve": "CVE-2021-33193",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2021-26690",
                    "cve": "CVE-2021-26690",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-17567",
                    "cve": "CVE-2019-17567",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-10081",
                    "cve": "CVE-2019-10081",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0220",
                    "cve": "CVE-2019-0220",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0196",
                    "cve": "CVE-2019-0196",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2018-17199",
                    "cve": "CVE-2018-17199",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2018-17189",
                    "cve": "CVE-2018-17189",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-0197",
                    "cve": "CVE-2019-0197",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2020-11993",
                    "cve": "CVE-2020-11993",
                },
                {
                    "model": Vulnerability,
                    "name": "CVE-2019-10092",
                    "cve": "CVE-2019-10092",
                },
            ],
        ),
        ToolTestCase(
            "ftp-vulnerabilities.xml",
            [
                {
                    "model": Host,
                    "ip": "10.10.10.10",
                    "os": "Apple macOS 10.13 (High Sierra) - 10.15 (Catalina) or iOS 11.0 - 13.4 (Darwin 17.0.0 - 19.2.0)",
                    "os_type": HostOS.IOS,
                },
                {
                    "model": Port,
                    "port": 21,
                    "status": PortStatus.OPEN,
                    "protocol": Protocol.TCP,
                    "service": "ftp",
                },
                {"model": Technology, "name": "vsftpd", "version": "2.3.4"},
                {
                    "model": Vulnerability,
                    "name": "vsFTPd Backdoor",
                    "cve": "CVE-2011-2523",
                },
                {
                    "model": Vulnerability,
                    "name": "Anonymous FTP",
                    "description": "Anonymous login is allowed in FTP",
                    "severity": Severity.CRITICAL,
                    "cwe": "CWE-287",
                    "reference": "https://book.hacktricks.xyz/pentesting/pentesting-ftp#anonymous-login",
                },
            ],
        ),
        ToolTestCase(
            "smb-analysis.xml",
            [
                {
                    "model": Host,
                    "ip": "10.10.10.10",
                    "os": "Apple macOS 10.13 (High Sierra) - 10.15 (Catalina) or iOS 11.0 - 13.4 (Darwin 17.0.0 - 19.2.0)",
                    "os_type": HostOS.IOS,
                },
                {
                    "model": Port,
                    "port": 445,
                    "status": PortStatus.OPEN,
                    "protocol": Protocol.TCP,
                    "service": "netbios-ssn",
                },
                {
                    "model": Technology,
                    "name": "Samba smbd",
                    "version": "3.X - 4.X",
                    # Description is none
                    "description": "Protocols: NT LM 0.12 (SMBv1), 2.0.2, 2.1, 3.0, 3.0.2, 3.1.1",
                },
                {
                    "model": Path,
                    "path": "IPC$",
                    "extra_info": (
                        "IPC Service (Samba Server Version 4.6.3) Type: STYPE_IPC_HIDDEN "
                        "Anonymous access: READ/WRITE Current access: READ/WRITE"
                    ),
                    "type": PathType.SHARE,
                },
                {
                    "model": Vulnerability,
                    "name": "Anonymous SMB",
                    "description": "Anonymous access is allowed to the SMB share IPC$",
                    "severity": Severity.CRITICAL,
                    "cwe": "CWE-287",
                },
                {
                    "model": Path,
                    "path": "myshare",
                    "extra_info": "Type: STYPE_DISKTREE Anonymous access: READ/WRITE Current access: READ/WRITE",
                    "type": PathType.SHARE,
                },
                {
                    "model": Vulnerability,
                    "name": "Anonymous SMB",
                    "description": "Anonymous access is allowed to the SMB share myshare",
                    "severity": Severity.CRITICAL,
                    "cwe": "CWE-287",
                },
            ],
        ),
        ToolTestCase(
            "smb-users.xml",
            [
                {
                    "model": Host,
                    "ip": "10.10.10.10",
                    "os": "Apple macOS 10.13 (High Sierra) - 10.15 (Catalina) or iOS 11.0 - 13.4 (Darwin 17.0.0 - 19.2.0)",
                    "os_type": HostOS.IOS,
                },
                {
                    "model": Port,
                    "port": 445,
                    "status": PortStatus.OPEN,
                    "protocol": Protocol.TCP,
                    "service": "netbios-ssn",
                },
                {"model": Technology, "name": "Samba smbd", "version": "3.X - 4.X"},
                {"model": Credential, "username": "629F42ED79BB\\test"},
                {
                    "model": Path,
                    "path": "IPC$",
                    "extra_info": (
                        "IPC Service (Samba 4.5.4) Type: STYPE_IPC_HIDDEN "
                        "Anonymous access: READ/WRITE Current access: READ/WRITE"
                    ),
                    "type": PathType.SHARE,
                },
                {
                    "model": Vulnerability,
                    "name": "Anonymous SMB",
                    "description": "Anonymous access is allowed to the SMB share IPC$",
                    "severity": Severity.CRITICAL,
                    "cwe": "CWE-287",
                },
                {
                    "model": Path,
                    "path": "shared",
                    "extra_info": "Type: STYPE_DISKTREE Anonymous access: READ/WRITE Current access: READ/WRITE",
                    "type": PathType.SHARE,
                },
                {
                    "model": Vulnerability,
                    "name": "Anonymous SMB",
                    "description": "Anonymous access is allowed to the SMB share shared",
                    "severity": Severity.CRITICAL,
                    "cwe": "CWE-287",
                },
            ],
        ),
    ]
