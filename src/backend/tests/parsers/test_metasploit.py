from findings.models import Exploit
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class MetasploitTest(ToolTest):
    tool_name = "Metasploit"
    cases = [
        ToolTestCase(
            "2022-exploits.txt",
            [
                {
                    "model": Exploit,
                    "title": "HP Data Protector Encrypted Communication Remote Command Execution",
                    "reference": "exploit/windows/misc/hp_dataprotector_encrypted_comms",
                },
                {
                    "model": Exploit,
                    "title": "Ruby on Rails ActionPack Inline ERB Code Execution",
                    "reference": "exploit/multi/http/rails_actionpack_inline_exec",
                },
                {
                    "model": Exploit,
                    "title": "Xymon Daemon Gather Information",
                    "reference": "auxiliary/gather/xymon_info",
                },
                {
                    "model": Exploit,
                    "title": "Xymon useradm Command Execution",
                    "reference": "exploit/unix/webapp/xymon_useradm_cmd_exec",
                },
            ],
        ),
        ToolTestCase(
            "2025-exploits.txt",
            [
                {
                    "model": Exploit,
                    "title": "Log4Shell HTTP Header Injection",
                    "reference": "exploit/multi/http/log4shell_header_injection",
                },
                {
                    "model": Exploit,
                    "title": "Log4Shell HTTP Scanner",
                    "reference": "auxiliary/scanner/http/log4shell_scanner",
                },
                {
                    "model": Exploit,
                    "title": "MobileIron Core Unauthenticated JNDI Injection RCE (via Log4Shell)",
                    "reference": "exploit/linux/http/mobileiron_core_log4shell",
                },
                {
                    "model": Exploit,
                    "title": "UniFi Network Application Unauthenticated JNDI Injection RCE (via Log4Shell)",
                    "reference": "exploit/multi/http/ubiquiti_unifi_log4shell",
                },
                {
                    "model": Exploit,
                    "title": "VMware vCenter Server Unauthenticated JNDI Injection RCE (via Log4Shell)",
                    "reference": "exploit/multi/http/vmware_vcenter_log4shell",
                },
            ],
        ),
        ToolTestCase("nothing.txt"),
    ]
