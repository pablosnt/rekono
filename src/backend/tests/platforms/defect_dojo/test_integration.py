from unittest import mock

from platforms.defect_dojo.integrations import DefectDojo
from platforms.defect_dojo.models import DefectDojoTargetSync
from tests.cases import ApiTestCase
from tests.framework import RekonoTest
from tests.platforms.defect_dojo.mock import (
    create_endpoint,
    create_finding,
    import_scan,
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
        "platforms.defect_dojo.integrations.DefectDojo._create_endpoint",
        create_endpoint,
    )
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo._create_finding", create_finding
    )
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo._import_scan", import_scan
    )
    def test_project_sync(self) -> None:
        ApiTestCase(
            ["admin1"], "post", 201, sync, {"id": 1, **sync}, "/api/defect-dojo/sync/"
        ).test_case()
        self._setup_findings(self.execution3)
        DefectDojo().process_findings(self.execution3, self.findings)
        self.assertEqual(1, self.execution3.defect_dojo_test_id)
        for finding in self.findings:
            self.assertIsNone(finding.defect_dojo_id)

    def test_target_sync(self) -> None:
        sync["engagement_id"] = None
        ApiTestCase(
            ["admin1"], "post", 201, sync, {"id": 1, **sync}, "/api/defect-dojo/sync/"
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
