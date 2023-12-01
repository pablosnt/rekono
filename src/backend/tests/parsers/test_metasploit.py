from findings.models import Exploit
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class MetasploitTest(ToolTest):
    tool_name = "Metasploit"
    cases = [
        ToolTestCase(
            "exploits.txt",
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
        ToolTestCase("nothing.txt"),
    ]
