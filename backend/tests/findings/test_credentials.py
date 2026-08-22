from django.test import TestCase

from findings.enums import Severity, TransportProtocol
from findings.models import Credential
from tests.findings.base import FindingTest

# pytype: disable=wrong-arg-types,attribute-error


class CredentialTest(FindingTest, TestCase):
    model = Credential
    endpoint = "/api/credentials/"
    expected_defectdojo = {
        "title": "Credentials exposure",
        "description": "Technology: WordPress\nEmail: admin10@rekono.dev\nUsername: admin10\nSecret: admin",
        "cwe": 200,
        "severity": str(Severity.HIGH),
    }
    expected_string = (
        f"10.10.10.10 - 80 - {TransportProtocol.TCP.value} - WordPress - 1.0.10 - admin10@rekono.dev - admin10 - admin"
    )

    def test_deduplication(self):
        first = Credential.objects.create_finding(
            self.execution,
            technology=self.technology,
            email="root@rekono.dev",
            username="root",
            secret="toor",
            context="Found in backup file",
        )
        second = Credential.objects.create_finding(
            self.execution, technology=self.technology, email="root@rekono.dev", username="root", secret="toor"
        )
        self.assertEqual(first.id, second.id)
        self.assertEqual(
            1,
            Credential.objects.filter(
                technology=self.technology, email="root@rekono.dev", username="root", secret="toor"
            ).count(),
        )
        self.assertEqual("Found in backup file", second.context)
        self.assertNotEqual(
            second.id,
            Credential.objects.create_finding(
                self.execution, technology=self.technology, email="root@rekono.dev", username="root", secret="different"
            ).id,
        )

    def test_deduplication_ignores_email_case(self):
        first = Credential.objects.create_finding(
            self.execution, technology=self.technology, email="Admin@Rekono.dev", username="operator", secret="s3cret"
        )
        second = Credential.objects.create_finding(
            self.execution, technology=self.technology, email="admin@rekono.dev", username="operator", secret="s3cret"
        )
        self.assertEqual(first.id, second.id)
        self.assertEqual(
            1,
            Credential.objects.filter(
                technology=self.technology, email__iexact="admin@rekono.dev", username="operator", secret="s3cret"
            ).count(),
        )
