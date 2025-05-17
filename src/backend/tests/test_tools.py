from typing import Any

from tests.cases import ApiTestCase
from tests.framework import ApiTest
from tools.enums import Intensity as IntensityEnum
from tools.models import Argument, Configuration, Input, Intensity, Output, Tool

# pytype: disable=wrong-arg-types

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
            "get",
            200,
            endpoint="{endpoint}?like=true",
        ),
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
            expected=[
                {
                    "id": 1,
                    "name": nmap,
                    "command": nmap.lower(),
                    "likes": 4,
                    "liked": True,
                }
            ],
            endpoint="{endpoint}?like=true",
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
        ApiTestCase(["reader1", "reader2"], "delete", 403, endpoint="{endpoint}1/like/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "delete",
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
                "likes": 0,
                "liked": False,
            },
            endpoint="{endpoint}1/",
        ),
    ]

    def _get_object(self) -> Any:
        return Tool.objects.get(pk=1)


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
        return Configuration.objects.get(pk=1)


class IntensityTest(ApiTest):
    expected_str = f"{nmap} - {IntensityEnum.SNEAKY.name}"

    def _get_object(self) -> Any:
        return Intensity.objects.get(pk=1)


class ArgumentTest(ApiTest):
    expected_str = f"{nmap} - host"

    def _get_object(self) -> Any:
        return Argument.objects.get(pk=1)


class InputTest(ApiTest):
    expected_str = f"{nmap} - host - Host"

    def _get_object(self) -> Any:
        return Input.objects.get(pk=1)


class OutputTest(ApiTest):
    expected_str = f"{nmap} - {first_nmap_configuration} - Host"

    def _get_object(self) -> Any:
        return Output.objects.get(pk=1)
