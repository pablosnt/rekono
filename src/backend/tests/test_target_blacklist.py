from typing import Any

from target_denylist.models import TargetDenylist
from tests.cases import ApiTestCase
from tests.framework import ApiTest

# pytype: disable=wrong-arg-types

default_denylist_1 = {"id": 1, "default": True, "target": "127.0.0.1"}
target_denylist1 = {"target": "rekono.com"}
target_denylist2 = {"target": ".*\.rekono\.com"}
invalid_regex_denylist = {"target": "*.rekono.com"}
target_denylist3 = {"target": "10.10.10.0/24"}
new_target_denylist = {"target": ".*\.new\.rekono.com"}
invalid_denylist = {"target": "*.rekono;com"}


class TargetDenylistTest(ApiTest):
    endpoint = "/api/target-denylist/"
    expected_str = default_denylist_1["target"]
    cases = [
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "get", 403),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "get",
            403,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected=default_denylist_1,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin1", "admin2"], "post", 400, data=invalid_denylist),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "post",
            403,
            data=target_denylist1,
        ),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            data=target_denylist1,
            expected={"id": 14, "default": False, **target_denylist1},
        ),
        ApiTestCase(["admin2"], "post", 400, data=target_denylist1),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={"id": 14, "default": False, **target_denylist1},
            endpoint="{endpoint}14/",
        ),
        ApiTestCase(
            ["admin2"],
            "post",
            201,
            data=target_denylist2,
            expected={"id": 15, "default": False, **target_denylist2},
        ),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            data=target_denylist3,
            expected={"id": 16, "default": False, **target_denylist3},
        ),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            data=invalid_regex_denylist,
            expected={"id": 17, "default": False, **invalid_regex_denylist},
        ),
        ApiTestCase(
            ["admin1", "auditor1"],
            "post",
            400,
            {"project": 1, "target": "rekono.com"},
            endpoint="/api/targets/",
        ),
        ApiTestCase(
            ["admin1", "auditor1"],
            "post",
            400,
            {"project": 1, "target": "subdomain.rekono.com"},
            endpoint="/api/targets/",
        ),
        ApiTestCase(
            ["admin1", "auditor1"],
            "post",
            400,
            {"project": 1, "target": "10.10.10.1"},
            endpoint="/api/targets/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            404,
            data=new_target_denylist,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            data=new_target_denylist,
            expected={"id": 14, "default": False, **new_target_denylist},
            endpoint="{endpoint}14/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={"id": 14, "default": False, **new_target_denylist},
            endpoint="{endpoint}14/",
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "delete",
            403,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin1", "admin2"], "delete", 404, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "delete",
            403,
            endpoint="{endpoint}14/",
        ),
        ApiTestCase(["admin2"], "delete", 204, endpoint="{endpoint}14/"),
        ApiTestCase(["admin1"], "delete", 404, endpoint="{endpoint}14/"),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}15/"),
        ApiTestCase(["admin2"], "delete", 204, endpoint="{endpoint}16/"),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}17/"),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected=default_denylist_1,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin1", "admin2"], "get", 404, endpoint="{endpoint}14/"),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_project()

    def _get_object(self) -> Any:
        return TargetDenylist.objects.first()
