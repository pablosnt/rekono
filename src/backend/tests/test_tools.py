from functools import cached_property

from django.test import TestCase

from security.authorization.roles import Role
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase
from tools.enums import Intensity as IntensityEnum
from tools.models import Argument, Configuration, Input, Intensity, Output, Tool

# pytype: disable=wrong-arg-types

nmap = "Nmap"
the_harvester = "theHarvester"


class ToolTest(ApiTestNoData, TestCase):
    endpoint = "/api/tools/"
    expected_string = nmap
    cases = [
        ApiTestCase([Role.READER], 403, endpoint="1"),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={"id": 1, "name": nmap, "command": nmap.lower(), "likes": 0, "liked": False},
            endpoint="1",
        ),
        PostApiTestCase([Role.READER], 403, endpoint="1/like"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR], endpoint=f"{endpoint}?like=true"),
        PostApiTestCase([Role.ADMIN, Role.AUDITOR], 204, endpoint="1/like"),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={
                "id": 1,
                "name": nmap,
                "command": nmap.lower(),
                "likes": 4,
                "liked": True,
            },
            endpoint="1",
        ),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected=[{"id": 1, "name": nmap, "command": nmap.lower(), "likes": 4, "liked": True}],
            endpoint=f"{endpoint}?like=true",
        ),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={"id": 3, "name": the_harvester, "command": the_harvester, "likes": 0, "liked": False},
            endpoint="3",
        ),
        DeleteApiTestCase([Role.READER], 403, endpoint="1/like"),
        DeleteApiTestCase([Role.ADMIN, Role.AUDITOR], endpoint="1/like"),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={"id": 1, "name": nmap, "command": nmap.lower(), "likes": 0, "liked": False},
            endpoint="1",
        ),
    ]

    @cached_property
    def object(self) -> Tool:
        return Tool.objects.get(pk=1)


first_nmap_configuration = "TCP ports"


class ConfigurationTest(ApiTestNoData, TestCase):
    endpoint = "/api/configurations/"
    expected_string = f"{nmap} - {first_nmap_configuration}"
    cases = [
        ApiTestCase([Role.READER], 403, endpoint="1"),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={"id": 1, "tool": {"id": 1, "name": nmap}, "name": first_nmap_configuration},
            endpoint="1",
        ),
    ]

    @cached_property
    def object(self) -> Configuration:
        return Configuration.objects.get(pk=1)


class IntensityTest(ApiTestNoData, TestCase):
    expected_string = f"{nmap} - {IntensityEnum.SNEAKY.name}"

    @cached_property
    def object(self) -> Intensity:
        return Intensity.objects.get(pk=1)


class ArgumentTest(ApiTestNoData, TestCase):
    expected_string = f"{nmap} - host"

    @cached_property
    def object(self) -> Argument:
        return Argument.objects.get(pk=1)


class InputTest(ApiTestNoData, TestCase):
    expected_string = f"{nmap} - host - Host"

    @cached_property
    def object(self) -> Input:
        return Input.objects.get(pk=1)


class OutputTest(ApiTestNoData, TestCase):
    expected_string = f"{nmap} - {first_nmap_configuration} - Host"

    @cached_property
    def object(self) -> Output:
        return Output.objects.get(pk=1)
