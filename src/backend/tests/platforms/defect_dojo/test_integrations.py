from unittest import mock

from platforms.defect_dojo.integrations import DefectDojo
from platforms.defect_dojo.models import DefectDojoTargetSync
from tests.cases import ApiTestCase
from tests.framework import RekonoTest
from tests.platforms.defect_dojo.mock import (
    create_engagement,
    create_test,
    create_test_type,
    import_scan,
    return_id,
    return_true,
)

sync = {
    "project": 1,
    "product_type_id": 1,
    "product_id": 1,
    "engagement_id": 1,
}


class DefectDojoIntegrationTest(RekonoTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()

    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo.is_available", return_true
    )
    @mock.patch("platforms.defect_dojo.integrations.DefectDojo.exists", return_true)
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo._import_scan", import_scan
    )
    def test_project_sync(self) -> None:
        ApiTestCase(
            ["admin1"], "post", 201, sync, {"id": 1, **sync}, "/api/defect-dojo/sync/"
        ).test_case()
        self._setup_findings(self.execution3)
        self.execution3.output_file = (
            self.data_dir / "reports" / "nmap" / "enumeration-vulners.xml"
        )
        DefectDojo().process_findings(self.execution3, self.findings)
        self.assertEqual(1, self.execution3.defect_dojo_test_id)
        for finding in self.findings:
            self.assertIsNone(finding.defect_dojo_id)

    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo.is_available", return_true
    )
    @mock.patch("platforms.defect_dojo.integrations.DefectDojo.exists", return_true)
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo.create_engagement",
        create_engagement,
    )
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo._create_test_type",
        create_test_type,
    )
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo._create_test",
        create_test,
    )
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo._create_endpoint",
        return_id,
    )
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo._create_finding", return_id
    )
    def test_target_sync(self) -> None:
        sync["engagement_id"] = None
        ApiTestCase(
            ["auditor1"], "post", 201, sync, {"id": 1, **sync}, "/api/defect-dojo/sync/"
        ).test_case()
        self.assertFalse(
            DefectDojoTargetSync.objects.filter(
                target=self.execution1.task.target
            ).exists()
        )
        self._setup_findings(self.execution1)
        integration = DefectDojo()
        integration.process_findings(self.execution1, self.findings)
        self.assertTrue(
            DefectDojoTargetSync.objects.filter(
                target=self.execution1.task.target
            ).exists()
        )
        self.assertIsNone(self.execution3.defect_dojo_test_id)
        for finding in self.findings:
            self.assertEqual(1, finding.defect_dojo_id)
        integration.process_findings(self.execution1, self.findings)
        self.assertEqual(
            1,
            DefectDojoTargetSync.objects.filter(
                target=self.execution1.task.target
            ).count(),
        )
        self.assertIsNone(self.execution3.defect_dojo_test_id)
        for finding in self.findings:
            self.assertEqual(1, finding.defect_dojo_id)
