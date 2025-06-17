from findings.enums import PathType
from findings.models import Path
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class SmbmapTest(ToolTest):
    tool_name = "SMBMap"
    cases = [
        ToolTestCase(
            "shares.csv",
            [
                {
                    "model": Path,
                    "path": "shared",
                    "extra_info": "READ_WRITE",
                    "type": PathType.SHARE,
                },
                {
                    "model": Path,
                    "path": "IPC$",
                    "extra_info": "NO_ACCESS - IPC Service (Samba 4.5.4)",
                    "type": PathType.SHARE,
                },
            ],
        )
    ]
