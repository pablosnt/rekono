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
                {"id": 10, "enabled": False},
                {"id": 9, "enabled": True},
                {"id": 8, "enabled": True},
                {"id": 7, "enabled": True},
                {"id": 6, "enabled": True},
                {"id": 5, "enabled": False},
                {"id": 4, "enabled": False},
                {"id": 3, "enabled": True},
                {"id": 2, "enabled": True},
                {"id": 1, "enabled": False},
            ],
        ),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, endpoint="defectdojo"),
        PutApiTestCase(
            [Role.ADMIN], data={"enabled": True}, expected={"id": 1, "enabled": True}, endpoint="defectdojo"
        ),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR, Role.READER],
            expected=[
                {"id": 10, "enabled": False},
                {"id": 9, "enabled": True},
                {"id": 8, "enabled": True},
                {"id": 7, "enabled": True},
                {"id": 6, "enabled": True},
                {"id": 5, "enabled": False},
                {"id": 4, "enabled": False},
                {"id": 3, "enabled": True},
                {"id": 2, "enabled": True},
                {"id": 1, "enabled": True},
            ],
        ),
    ]

    @cached_property
    def object(self) -> Integration:
        return Integration.objects.first()
