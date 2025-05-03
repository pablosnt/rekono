from typing import Any, Optional

from reporting.enums import FindingName, ReportFormat
from reporting.models import Report
from targets.enums import TargetType
from targets.models import Target
from tests.cases import ApiTestCase
from tests.framework import ApiTest


class ReportingTest(ApiTest):
    endpoint = "/api/reports/"
    format = None
    only_true_positives = False
    finding_types: Optional[list[str]] = [
        FindingName.OSINT.value,
        FindingName.HOST.value,
        FindingName.PORT.value,
        FindingName.PATH.value,
        FindingName.CREDENTIAL.value,
        FindingName.TECHNOLOGY.value,
        FindingName.VULNERABILITY.value,
        FindingName.EXPLOIT.value,
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
        self._setup_findings(self.execution1)

    def test_cases(self) -> None:
        if self.format:
            report = {
                "format": self.format.value,
                "only_true_positives": self.only_true_positives,
            }
            if self.finding_types:
                report["finding_types"] = self.finding_types
            self.cases = [
                ApiTestCase(
                    ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
                    "get",
                    200,
                    expected=[],
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "post",
                    403,
                    {**report, "project": 1},
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "post",
                    403,
                    {**report, "target": 1},
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "post",
                    403,
                    {**report, "task": 1},
                ),
                ApiTestCase(["admin1", "auditor1", "reader1"], "post", 400, report),
                ApiTestCase(
                    ["admin1"],
                    "post",
                    201,
                    {**report, "project": 1},
                    expected={
                        "id": 1,
                        "project": 1,
                        "task": None,
                        "target": None,
                        "format": self.format.value,
                        "user": 1,
                    },
                ),
                ApiTestCase(
                    ["auditor1"],
                    "post",
                    201,
                    {**report, "task": 1},
                    expected={
                        "id": 2,
                        "project": None,
                        "task": 1,
                        "target": None,
                        "format": self.format.value,
                        "user": 3,
                    },
                ),
                ApiTestCase(
                    ["reader1"],
                    "post",
                    201,
                    {**report, "target": 1},
                    expected={
                        "id": 3,
                        "project": None,
                        "task": None,
                        "target": 1,
                        "format": self.format.value,
                        "user": 5,
                    },
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "get",
                    404,
                    endpoint="{endpoint}1/",
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "get",
                    404,
                    endpoint="{endpoint}2/",
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "get",
                    404,
                    endpoint="{endpoint}3/",
                ),
                ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200, expected=[]),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    200,
                    expected={
                        "id": 1,
                        "project": {"id": 1, "name": "test"},
                        "task": None,
                        "target": None,
                        "format": self.format.value,
                        "user": {"id": 1, "username": "admin1"},
                    },
                    endpoint="{endpoint}1/",
                ),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    200,
                    expected={
                        "id": 2,
                        "project": None,
                        "task": {"id": 1, "target": {"id": 1}},
                        "target": None,
                        "format": self.format.value,
                        "user": {"id": 3, "username": "auditor1"},
                    },
                    endpoint="{endpoint}2/",
                ),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    200,
                    expected={
                        "id": 3,
                        "project": None,
                        "task": None,
                        "target": {"id": 1},
                        "format": self.format.value,
                        "user": {"id": 5, "username": "reader1"},
                    },
                    endpoint="{endpoint}3/",
                ),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    200,
                    expected=[
                        {
                            "id": 3,
                            "project": None,
                            "task": None,
                            "target": {"id": 1},
                            "format": self.format.value,
                            "user": {"id": 5, "username": "reader1"},
                        },
                        {
                            "id": 2,
                            "project": None,
                            "task": {"id": 1, "target": {"id": 1}},
                            "target": None,
                            "format": self.format.value,
                            "user": {"id": 3, "username": "auditor1"},
                        },
                        {
                            "id": 1,
                            "project": {"id": 1, "name": "test"},
                            "task": None,
                            "target": None,
                            "format": self.format.value,
                            "user": {"id": 1, "username": "admin1"},
                        },
                    ],
                ),
                # Downloads return a 400 error because reports are created within a thread execution and having two
                # threads working on the same tables at the same time is not compatible with SQLite
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    400,
                    endpoint=f"{self.endpoint}1/download/",
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "get",
                    404,
                    endpoint=f"{self.endpoint}1/download/",
                ),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    400,
                    endpoint=f"{self.endpoint}2/download/",
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "get",
                    404,
                    endpoint=f"{self.endpoint}2/download/",
                ),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    400,
                    endpoint=f"{self.endpoint}3/download/",
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "get",
                    404,
                    endpoint=f"{self.endpoint}3/download/",
                ),
                ApiTestCase(
                    ["auditor2", "reader2"], "delete", 404, endpoint="{endpoint}1/"
                ),
                ApiTestCase(
                    ["auditor1", "reader1"], "delete", 403, endpoint="{endpoint}1/"
                ),
                ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}1/"),
                ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}2/"),
                ApiTestCase(["reader1"], "delete", 204, endpoint="{endpoint}3/"),
                ApiTestCase(
                    [
                        "admin1",
                        "admin2",
                        "auditor1",
                        "auditor2",
                        "reader1",
                        "reader2",
                    ],
                    "get",
                    404,
                    endpoint="{endpoint}1/",
                ),
                ApiTestCase(
                    [
                        "admin1",
                        "admin2",
                        "auditor1",
                        "auditor2",
                        "reader1",
                        "reader2",
                    ],
                    "get",
                    404,
                    endpoint="{endpoint}2/",
                ),
                ApiTestCase(
                    [
                        "admin1",
                        "admin2",
                        "auditor1",
                        "auditor2",
                        "reader1",
                        "reader2",
                    ],
                    "get",
                    404,
                    endpoint="{endpoint}3/",
                ),
                ApiTestCase(
                    [
                        "admin1",
                        "admin2",
                        "auditor1",
                        "auditor2",
                        "reader1",
                        "reader2",
                    ],
                    "get",
                    200,
                    expected=[],
                ),
            ]
            super().test_cases()

    def test_str(self) -> None:
        if self.format:
            self.expected_str = (
                f"{self.project.name} - {self.format.value} - {self.admin1.email}"
            )
            super().test_str()

    def _get_object(self) -> Any:
        return Report(format=self.format, project=self.project, user=self.admin1)


class JsonReportTest(ReportingTest):
    format = ReportFormat.JSON


class JsonReportTruePositivesTest(ReportingTest):
    format = ReportFormat.JSON
    only_true_positives = False


class XmlReportTest(ReportingTest):
    format = ReportFormat.XML


class XmlReportTruePositivesTest(ReportingTest):
    format = ReportFormat.XML
    only_true_positives = False


class PdfReportTest(ReportingTest):
    format = ReportFormat.PDF
    finding_types = None

    def setUp(self) -> None:
        super().setUp()
        Target.objects.create(
            project=self.project, target="10.10.10.15", type=TargetType.PRIVATE_IP
        )


class PdfReportWithoutFindingsTest(ApiTest):
    endpoint = "/api/reports/"
    cases = [
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "post",
            404,
            {
                "format": ReportFormat.PDF.value,
                "only_true_positives": True,
                "project": 1,
            },
        )
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
