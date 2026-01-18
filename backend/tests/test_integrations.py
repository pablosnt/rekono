from functools import cached_property

from django.test import TestCase

from integrations.models import Integration
from security.authorization.roles import Role
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase, PutApiTestCase

# pytype: disable=wrong-arg-types


class IntegrationTest(ApiTestNoData, TestCase):
    endpoint = "/api/integrations/"
    expected_string = "DefectDojo"
    cases = [
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR, Role.READER],
            expected=[
                {"id": 5, "enabled": True},
                {"id": 4, "enabled": True},
                {"id": 3, "enabled": True},
                {"id": 2, "enabled": True},
                {"id": 1, "enabled": True},
            ],
        ),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, endpoint="1"),
        PutApiTestCase([Role.ADMIN], data={"enabled": False}, expected={"id": 1, "enabled": False}, endpoint="1"),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR, Role.READER],
            expected=[
                {"id": 5, "enabled": True},
                {"id": 4, "enabled": True},
                {"id": 3, "enabled": True},
                {"id": 2, "enabled": True},
                {"id": 1, "enabled": False},
            ],
        ),
    ]

    @cached_property
    def object(self) -> Integration:
        return Integration.objects.first()
