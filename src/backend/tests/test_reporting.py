from functools import cached_property

from django.test import TestCase

from reporting.enums import FindingName, ReportFormat
from reporting.models import Report
from security.authorization.roles import Role
from targets.enums import TargetType
from targets.models import Target
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types,attribute-error


class ReportingTest(ApiTest):
    endpoint = "/api/reports/"
    format = None
    only_true_positives = False
    finding_types: list[str] | None = [name.value for name in FindingName]

    def test_cases(self) -> None:
        if self.format:
            report = {"format": self.format.value, "only_true_positives": self.only_true_positives}
            if self.finding_types:
                report["finding_types"] = self.finding_types
            self.cases = [
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
                PostApiTestCase(["not_members"], 403, {**report, "project": 1}),
                PostApiTestCase(["not_members"], 403, {**report, "target": 1}),
                PostApiTestCase(["not_members"], 403, {**report, "task": 1}),
                PostApiTestCase(["members"], 400, report),
                PostApiTestCase(
                    ["admin1"],
                    data={**report, "project": 1},
                    expected={
                        "id": 1,
                        "project": 1,
                        "task": None,
                        "target": None,
                        "format": self.format.value,
                        "user": 1,
                    },
                ),
                PostApiTestCase(
                    ["auditor1"],
                    data={**report, "task": 1},
                    expected={
                        "id": 2,
                        "project": None,
                        "task": 1,
                        "target": None,
                        "format": self.format.value,
                        "user": 3,
                    },
                ),
                PostApiTestCase(
                    ["reader1"],
                    data={**report, "target": 1},
                    expected={
                        "id": 3,
                        "project": None,
                        "task": None,
                        "target": 1,
                        "format": self.format.value,
                        "user": 5,
                    },
                ),
                ApiTestCase(["not_members"], 404, endpoint="1"),
                ApiTestCase(["not_members"], 404, endpoint="2"),
                ApiTestCase(["not_members"], 404, endpoint="3"),
                ApiTestCase(["not_members"]),
                ApiTestCase(
                    ["members"],
                    expected={
                        "id": 1,
                        "project": {"id": 1},
                        "task": None,
                        "target": None,
                        "format": self.format.value,
                        "user": {"id": 1, "username": "admin1"},
                    },
                    endpoint="1",
                ),
                ApiTestCase(
                    ["members"],
                    expected={
                        "id": 2,
                        "project": None,
                        "task": {"id": 1, "target": {"id": 1}},
                        "target": None,
                        "format": self.format.value,
                        "user": {"id": 3, "username": "auditor1"},
                    },
                    endpoint="2",
                ),
                ApiTestCase(
                    ["members"],
                    expected={
                        "id": 3,
                        "project": None,
                        "task": None,
                        "target": {"id": 1},
                        "format": self.format.value,
                        "user": {"id": 5, "username": "reader1"},
                    },
                    endpoint="3",
                ),
                ApiTestCase(
                    ["members"],
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
                            "project": {"id": 1},
                            "task": None,
                            "target": None,
                            "format": self.format.value,
                            "user": {"id": 1, "username": "admin1"},
                        },
                    ],
                ),
                # Downloads return a 400 error because reports are created within a thread execution and having two
                # threads working on the same tables at the same time is not compatible with SQLite
                ApiTestCase(["members"], 400, endpoint="1/download"),
                ApiTestCase(["not_members"], 404, endpoint="1/download"),
                ApiTestCase(["members"], 400, endpoint="2/download"),
                ApiTestCase(["not_members"], 404, endpoint="2/download"),
                ApiTestCase(["members"], 400, endpoint="3/download"),
                ApiTestCase(["not_members"], 404, endpoint="3/download"),
                DeleteApiTestCase(["auditor2", "reader2"], 404, endpoint="1"),
                DeleteApiTestCase(["auditor1", "reader1"], 403, endpoint="1"),
                DeleteApiTestCase(["admin1"], endpoint="1"),
                DeleteApiTestCase(["admin1"], endpoint="2"),
                DeleteApiTestCase(["reader1"], endpoint="3"),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="2"),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="3"),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
            ]
            super().test_cases()

    def test_string(self) -> None:
        if self.format:
            self.expected_string = f"{self.project.name} - {self.format.value} - {self.admin1.email}"
            super().test_string()

    @cached_property
    def object(self) -> Report:
        return Report(format=self.format, project=self.project, user=self.admin1)


class JsonReportTest(ReportingTest, TestCase):
    format = ReportFormat.JSON


class JsonReportTruePositivesTest(ReportingTest, TestCase):
    format = ReportFormat.JSON
    only_true_positives = False


class XmlReportTest(ReportingTest, TestCase):
    format = ReportFormat.XML


class XmlReportTruePositivesTest(ReportingTest, TestCase):
    format = ReportFormat.XML
    only_true_positives = False


class PdfReportTest(ReportingTest, TestCase):
    format = ReportFormat.PDF
    finding_types = None

    def setup_testing_data(self) -> None:
        super().setup_testing_data()
        Target.objects.create(project=self.project, target="10.10.10.15", type=TargetType.PRIVATE_IP)


class PdfReportWithoutFindingsTest(ApiTest, TestCase):
    endpoint = "/api/reports/"
    data = [SetupProject(executions_per_task=0)]
    cases = [
        PostApiTestCase(
            ["members"],
            404,
            data={"format": ReportFormat.PDF.value, "only_true_positives": True, "project": 1},
        )
    ]
