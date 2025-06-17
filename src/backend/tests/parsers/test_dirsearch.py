from findings.enums import PathType
from findings.models import Path
from tests.cases import ToolTestCase
from tests.framework import ToolTest

expected = [
    {
        "model": Path,
        "path": "/.ht_wsr.txt",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htaccess.sample",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htaccess_orig",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htaccess.bak1",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htaccess_sc",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htaccess.save",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htaccess.orig",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htaccess_extra",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htm",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htaccessBAK",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.httr-oauth",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htaccessOLD2",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.html",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htaccessOLD",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htpasswds",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.htpasswd_test",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/.php",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/assets/",
        "status": 200,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/assets",
        "status": 301,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/index.html",
        "status": 200,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/server-status",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
    {
        "model": Path,
        "path": "/server-status/",
        "status": 403,
        "type": PathType.ENDPOINT,
    },
]


class DirsearchTest(ToolTest):
    tool_name = "Dirsearch"
    cases = [ToolTestCase("2022-default.json", expected), ToolTestCase("2025-default.json", expected)]
