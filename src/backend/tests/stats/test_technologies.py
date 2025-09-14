from tests.framework import StatsTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject


class TechnologyStatsTest(StatsTest):
    endpoint = "/api/stats/technology/"
    data = [
        SetupProject(
            _technologies_fields=[
                {"name": "WordPress"},
                {"name": "Apache"},
                {"name": "MySQL"},
                {"name": "WordPress"},
                {"name": "PHP"},
                {"name": "Nginx", "is_fixed": True},
            ]
        ),
        SetupProject(
            _technologies_fields=[{"name": "WordPress"}, {"name": "Node.js"}, {"name": "React"}, {"name": "MongoDB"}]
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
        ApiTestCase(["not_members"]),
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
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
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
        ApiTestCase(["not_members"], endpoint="{endpoint}?target=1"),
    ]
