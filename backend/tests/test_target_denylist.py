from functools import cached_property

from django.test import TestCase

from security.authorization.roles import Role
from target_denylist.models import TargetDenylist
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types

default_denylist_1 = {"id": 1, "default": True, "target": "127.0.0.1", "blocked": 0}
target_denylist1 = {"target": "rekono.com"}
target_denylist2 = {"target": ".*\.rekono\.com"}
invalid_regex_denylist = {"target": "*.rekono.com"}
target_denylist3 = {"target": "10.10.10.0/24"}
new_target_denylist = {"target": ".*\.new\.rekono.com"}
invalid_denylist = {"target": "*.rekono;com"}


class TargetDenylistTest(ApiTest, TestCase):
    endpoint = "/api/target-denylist/"
    expected_string = default_denylist_1["target"]
    data = [SetupProject(targets_and_tasks=0)]
    cases = [
        ApiTestCase([Role.AUDITOR, Role.READER], 403),
        ApiTestCase([Role.AUDITOR, Role.READER], 403, endpoint="1"),
        ApiTestCase([Role.ADMIN], 200, expected=default_denylist_1, endpoint="1"),
        PostApiTestCase([Role.ADMIN], 400, invalid_denylist),
        PostApiTestCase([Role.AUDITOR, Role.READER], 403, target_denylist1),
        PostApiTestCase(
            ["admin1"], data=target_denylist1, expected={"id": 14, "default": False, "blocked": 0, **target_denylist1}
        ),
        PostApiTestCase(["admin2"], 400, target_denylist1),
        ApiTestCase(
            [Role.ADMIN], expected={"id": 14, "default": False, "blocked": 0, **target_denylist1}, endpoint="14"
        ),
        PostApiTestCase(
            ["admin2"], data=target_denylist2, expected={"id": 15, "default": False, "blocked": 0, **target_denylist2}
        ),
        PostApiTestCase(
            ["admin1"], data=target_denylist3, expected={"id": 16, "default": False, "blocked": 0, **target_denylist3}
        ),
        PostApiTestCase(
            ["admin1"],
            data=invalid_regex_denylist,
            expected={"id": 17, "default": False, "blocked": 0, **invalid_regex_denylist},
        ),
        PostApiTestCase(["admin1", "auditor1"], 400, {"project": 1, "target": "rekono.com"}, endpoint="/api/targets/"),
        PostApiTestCase(["admin1", "auditor1"], 400, {"project": 1, "target": "REKONO.COM"}, endpoint="/api/targets/"),
        PostApiTestCase(["admin1", "auditor1"], 400, {"project": 1, "target": "rekono.com."}, endpoint="/api/targets/"),
        PostApiTestCase(
            ["admin1", "auditor1"], 400, {"project": 1, "target": "subdomain.rekono.com"}, endpoint="/api/targets/"
        ),
        PostApiTestCase(["admin1", "auditor1"], 400, {"project": 1, "target": "10.10.10.1"}, endpoint="/api/targets/"),
        PostApiTestCase(
            ["admin1", "auditor1"], 400, {"project": 1, "target": "127.0.0.1/32"}, endpoint="/api/targets/"
        ),
        PostApiTestCase(["admin1", "auditor1"], 400, {"project": 1, "target": "127.0.0.0/8"}, endpoint="/api/targets/"),
        PostApiTestCase(["admin1", "auditor1"], 400, {"project": 1, "target": "127.0.0.1-5"}, endpoint="/api/targets/"),
        PostApiTestCase(
            ["admin1", "auditor1"], 400, {"project": 1, "target": "::ffff:127.0.0.1"}, endpoint="/api/targets/"
        ),
        PostApiTestCase(["admin1", "auditor1"], 400, {"project": 1, "target": "10.0.0.0/8"}, endpoint="/api/targets/"),
        PostApiTestCase(
            ["admin1", "auditor1"], 400, {"project": 1, "target": "10.10.10.1-24"}, endpoint="/api/targets/"
        ),
        # Networks and IP ranges that don't reach any denied value are still allowed
        PostApiTestCase(
            ["admin1"],
            data={"project": 1, "target": "10.10.20.0/24"},
            expected={"target": "10.10.20.0/24"},
            endpoint="/api/targets/",
        ),
        ApiTestCase(
            [Role.ADMIN], expected={"id": 1, "default": True, "target": "127.0.0.1", "blocked": 8}, endpoint="1"
        ),
        ApiTestCase(
            [Role.ADMIN], expected={"id": 14, "default": False, "blocked": 6, **target_denylist1}, endpoint="14"
        ),
        ApiTestCase(
            [Role.ADMIN], expected={"id": 15, "default": False, "blocked": 2, **target_denylist2}, endpoint="15"
        ),
        ApiTestCase(
            [Role.ADMIN], expected={"id": 16, "default": False, "blocked": 6, **target_denylist3}, endpoint="16"
        ),
        PutApiTestCase([Role.ADMIN], 404, new_target_denylist, endpoint="1"),
        PutApiTestCase(
            [Role.ADMIN],
            data=new_target_denylist,
            expected={"id": 14, "default": False, "blocked": 6, **new_target_denylist},
            endpoint="14",
        ),
        ApiTestCase(
            [Role.ADMIN], expected={"id": 14, "default": False, "blocked": 6, **new_target_denylist}, endpoint="14"
        ),
        DeleteApiTestCase([Role.AUDITOR, Role.READER], 403, endpoint="1"),
        DeleteApiTestCase([Role.ADMIN], 404, endpoint="1"),
        DeleteApiTestCase([Role.AUDITOR, Role.READER], 403, endpoint="14"),
        DeleteApiTestCase(["admin2"], endpoint="14"),
        DeleteApiTestCase(["admin1"], 404, endpoint="14"),
        DeleteApiTestCase(["admin1"], endpoint="15"),
        DeleteApiTestCase(["admin2"], endpoint="16"),
        DeleteApiTestCase(["admin1"], endpoint="17"),
        ApiTestCase([Role.ADMIN], expected={**default_denylist_1, "blocked": 8}, endpoint="1"),
        ApiTestCase([Role.ADMIN], 404, endpoint="14"),
    ]

    @cached_property
    def object(self) -> TargetDenylist:
        return TargetDenylist.objects.first()
