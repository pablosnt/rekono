from functools import cached_property

from django.test import TestCase
from rest_framework.test import APIClient

from security.authorization.roles import Role
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase
from tools.enums import Intensity as IntensityEnum
from tools.models import Argument, Configuration, Input, Intensity, Output, Tool

# pytype: disable=wrong-arg-types

nmap = "Nmap"
gobuster = "Gobuster"


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
            expected={"id": 20, "name": gobuster, "command": gobuster.lower(), "likes": 0, "liked": False},
            endpoint="20",
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

    def test_configurations_exclude_deprecated(self) -> None:
        client = APIClient()
        client.force_authenticate(self.users[Role.ADMIN][0])
        configuration = Configuration.objects.filter(tool__pk=1).first()
        configuration.deprecated = True
        configuration.save(update_fields=["deprecated"])
        self.assertNotIn(configuration.pk, [c["id"] for c in client.get("/api/tools/1/").json()["configurations"]])


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

    def test_endpoint_excludes_deprecated(self) -> None:
        client = APIClient()
        client.force_authenticate(self.users[Role.ADMIN][0])
        configuration = Configuration.objects.filter(deprecated=False).first()
        configuration.deprecated = True
        configuration.save(update_fields=["deprecated"])
        self.assertEqual(404, client.get(f"/api/configurations/{configuration.pk}/").status_code)
        self.assertNotIn(
            configuration.pk,
            [s["id"] for s in client.get(f"/api/configurations/?tool={configuration.tool.id}").json()["results"]],
        )


class IntensityTest(ApiTestNoData, TestCase):
    expected_string = f"{nmap} - {IntensityEnum.SNEAKY.name}"

    @cached_property
    def object(self) -> Intensity:
        return Intensity.objects.get(pk=1)


class ArgumentTest(ApiTestNoData, TestCase):
    expected_string = f"{nmap} - {first_nmap_configuration} - host"

    @cached_property
    def object(self) -> Argument:
        return Argument.objects.get(pk=1)


class InputTest(ApiTestNoData, TestCase):
    expected_string = f"{nmap} - {first_nmap_configuration} - host - Host"

    @cached_property
    def object(self) -> Input:
        return Input.objects.get(pk=1)


class OutputTest(ApiTestNoData, TestCase):
    expected_string = f"{nmap} - {first_nmap_configuration} - Host"

    @cached_property
    def object(self) -> Output:
        return Output.objects.get(pk=1)
