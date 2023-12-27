from findings.enums import PathType
from findings.models import Path
from tests.cases import ToolTestCase
from tests.framework import ToolTest

expected_shares = [
    {
        "model": Path,
        "path": "shared",
        "extra_info": "READ, WRITE",
        "type": PathType.SHARE,
    },
    {
        "model": Path,
        "path": "IPC$",
        "extra_info": "[NO ACCESS] IPC Service (Samba 4.5.4)",
        "type": PathType.SHARE,
    },
]


class SmbmapTest(ToolTest):
    tool_name = "SMBMap"
    cases = [
        ToolTestCase("shares.txt", expected_shares),
        ToolTestCase("directories.txt", expected_shares),
    ]
