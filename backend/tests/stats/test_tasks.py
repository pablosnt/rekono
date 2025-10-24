from django.test import TestCase

from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


class LatestTasksTest(ApiTest, TestCase):
    endpoint = "/api/stats/latest-tasks/"
    data = [SetupProject(1, 0), SetupProject(6, 0)]
    cases = [
        ApiTestCase(["members"], expected=[{"id": value, "target": {"id": value}} for value in range(1, 6)]),
        ApiTestCase(["not_members"]),
        ApiTestCase(["members"], expected=[{"id": 1, "target": {"id": 1}}], endpoint="{endpoint}?project=1"),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
        ApiTestCase(["members"], expected=[{"id": 1, "target": {"id": 1}}], endpoint="{endpoint}?target=1"),
        ApiTestCase(
            ["members"],
            expected=[{"id": value, "target": {"id": value}} for value in range(2, 7)],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["members"], expected=[{"id": 2, "target": {"id": 2}}], endpoint="{endpoint}?target=2"),
    ]
