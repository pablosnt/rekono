from typing import Any

from tests.cases import ApiTestCase
from tests.framework import ApiTest
from tools.models import Configuration, Tool

nmap = "Nmap"
the_harvester = "theHarvester"


class ToolTest(ApiTest):
    endpoint = "/api/tools/"
    expected_str = nmap
    cases = [
        ApiTestCase(["reader1", "reader2"], "get", 403, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 1,
                "name": nmap,
                "command": nmap.lower(),
                "likes": 0,
                "liked": False,
            },
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["reader1", "reader2"], "post", 403, endpoint="{endpoint}1/like/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "post",
            204,
            endpoint="{endpoint}1/like/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 1,
                "name": nmap,
                "command": nmap.lower(),
                "likes": 4,
                "liked": True,
            },
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 3,
                "name": the_harvester,
                "command": the_harvester,
                "likes": 0,
                "liked": False,
            },
            endpoint="{endpoint}3/",
        ),
        ApiTestCase(
            ["reader1", "reader2"], "get", 403, endpoint="{endpoint}1/dislike/"
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "post",
            204,
            endpoint="{endpoint}1/dislike/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 1,
                "name": nmap,
                "command": nmap.lower(),
                "likes": 0,
                "liked": False,
            },
            endpoint="{endpoint}1/",
        ),
    ]

    def _get_object(self) -> Any:
        return Tool.objects.first()


first_nmap_configuration = "TCP ports"


class ConfigurationTest(ApiTest):
    endpoint = "/api/configurations/"
    expected_str = f"{nmap} - {first_nmap_configuration}"
    cases = [
        ApiTestCase(["reader1", "reader2"], "get", 403, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 1,
                "tool": {"id": 1, "name": nmap},
                "name": first_nmap_configuration,
            },
            endpoint="{endpoint}1/",
        ),
    ]

    def _get_object(self) -> Any:
        return Configuration.objects.first()
