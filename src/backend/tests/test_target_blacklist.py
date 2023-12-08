from typing import Any

from target_blacklist.models import TargetBlacklist
from tests.cases import ApiTestCase
from tests.framework import ApiTest

default_blacklist_1 = {"id": 1, "default": True, "target": "127.0.0.1"}
target_blacklist1 = {"target": "rekono.com"}
target_blacklist2 = {"target": ".*\.rekono\.com"}
target_blacklist3 = {"target": "10.10.10.0/24"}
new_target_blacklist = {"target": ".*\.new\.rekono.com"}
invalid_blacklist = {"target": "*.rekono;com"}


class TargetBlacklistTest(ApiTest):
    endpoint = "/api/target-blacklist/"
    expected_str = default_blacklist_1["target"]
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
            expected=default_blacklist_1,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin1", "admin2"], "post", 400, data=invalid_blacklist),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "post",
            403,
            data=target_blacklist1,
        ),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            data=target_blacklist1,
            expected={"id": 14, "default": False, **target_blacklist1},
        ),
        ApiTestCase(["admin2"], "post", 400, data=target_blacklist1),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={"id": 14, "default": False, **target_blacklist1},
            endpoint="{endpoint}14/",
        ),
        ApiTestCase(
            ["admin2"],
            "post",
            201,
            data=target_blacklist2,
            expected={"id": 15, "default": False, **target_blacklist2},
        ),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            data=target_blacklist3,
            expected={"id": 16, "default": False, **target_blacklist3},
        ),
        # ApiTestCase(
        #     ["admin1", "auditor1"],
        #     "post",
        #     400,
        #     {"project": 1, "target": "rekono.com"},
        #     endpoint="/api/targets/",
        # ),
        # ApiTestCase(
        #     ["admin1", "auditor1"],
        #     "post",
        #     400,
        #     {"project": 1, "target": "subdomain.rekono.com"},
        #     endpoint="/api/targets/",
        # ),
        # ApiTestCase(
        #     ["admin1", "auditor1"],
        #     "post",
        #     400,
        #     {"project": 1, "target": "10.10.10.1"},
        #     endpoint="/api/targets/",
        # ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            404,
            data=new_target_blacklist,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            data=new_target_blacklist,
            expected={"id": 14, "default": False, **new_target_blacklist},
            endpoint="{endpoint}14/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={"id": 14, "default": False, **new_target_blacklist},
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
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected=default_blacklist_1,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin1", "admin2"], "get", 404, endpoint="{endpoint}14/"),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_project()

    def _get_object(self) -> Any:
        return TargetBlacklist.objects.first()
