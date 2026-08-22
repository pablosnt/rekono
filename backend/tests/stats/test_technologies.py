from django.test import TestCase

from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject
from tests.stats.test_base import BaseStatsAuthorizationTest

# pytype: disable=wrong-arg-types


class TechnologyStatsTest(ApiTest, TestCase):
    endpoint = "/api/stats/technology/"
    data = [
        SetupProject(
            technologies_fields=[
                {"name": "WordPress"},
                {"name": "Apache"},
                {"name": "MySQL"},
                {"name": "WordPress"},
                {"name": "PHP"},
                {"name": "Nginx", "is_fixed": True},
            ]
        ),
        SetupProject(
            technologies_fields=[{"name": "WordPress"}, {"name": "Node.js"}, {"name": "React"}, {"name": "MongoDB"}]
        ),
        SetupProject(1, 0),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"name": "WordPress", "count": 3},
                {"name": "Apache", "count": 1},
                {"name": "MongoDB", "count": 1},
                {"name": "MySQL", "count": 1},
                {"name": "Node.js", "count": 1},
                {"name": "PHP", "count": 1},
                {"name": "React", "count": 1},
            ],
        ),
        ApiTestCase(["not_members"], expected=[]),
        ApiTestCase(
            ["members"],
            expected=[
                {"name": "WordPress", "count": 2},
                {"name": "Apache", "count": 1},
                {"name": "MySQL", "count": 1},
                {"name": "PHP", "count": 1},
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?project=1"),
        ApiTestCase(
            ["members"],
            expected=[
                {"name": "MongoDB", "count": 1},
                {"name": "Node.js", "count": 1},
                {"name": "React", "count": 1},
                {"name": "WordPress", "count": 1},
            ],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?project=2"),
        ApiTestCase(
            ["members"],
            expected=[
                {"name": "WordPress", "count": 2},
                {"name": "Apache", "count": 1},
                {"name": "MySQL", "count": 1},
                {"name": "PHP", "count": 1},
            ],
            endpoint="{endpoint}?target=1",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?target=1"),
        ApiTestCase(
            ["members"],
            expected=[
                {"name": "MongoDB", "count": 1},
                {"name": "Node.js", "count": 1},
                {"name": "React", "count": 1},
                {"name": "WordPress", "count": 1},
            ],
            endpoint="{endpoint}?target=2",
        ),
        ApiTestCase(["not_members"], expected=[], endpoint="{endpoint}?target=2"),
    ]


class TechnologyStatsAuthorizationTest(BaseStatsAuthorizationTest, TestCase):
    endpoint = "/api/stats/technology/"
    project_1_members_expected = [{"name": "WordPress", "count": 1}]
    project_2_members_expected = [{"name": "Nginx", "count": 1}]
