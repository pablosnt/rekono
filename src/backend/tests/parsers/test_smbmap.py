from findings.enums import PathType
from findings.models import Path
from tests.framework import ParserTest
from tests.framework.cases import ParserTestCase


class SmbmapTest(ParserTest):
    tool_name = "SMBMap"
    cases = [
        ParserTestCase(
            "shares.csv",
            [
                {"model": Path, "path": "shared", "extra_info": "READ_WRITE", "type": PathType.SHARE},
                {
                    "model": Path,
                    "path": "IPC$",
                    "extra_info": "NO_ACCESS - IPC Service (Samba 4.5.4)",
                    "type": PathType.SHARE,
                },
            ],
        )
    ]
