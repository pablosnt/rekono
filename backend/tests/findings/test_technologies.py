from django.test import TestCase

from findings.enums import Severity, TransportProtocol
from findings.models import Technology
from tests.findings.base import FindingTest
from tools.models import Input

# pytype: disable=wrong-arg-types,attribute-error


class TechnologyTest(FindingTest, TestCase):
    model = Technology
    endpoint = "/api/technologies/"
    expected_defectdojo = {
        "title": "Technology WordPress detected",
        "description": "Typical CMS\n\nTechnology: WordPress\nVersion: 1.0.10",
        "severity": str(Severity.LOW),
        "cwe": 200,
        "references": "https://wordpress.org",
    }
    expected_string = f"10.10.10.10 - 80 - {TransportProtocol.TCP.value} - WordPress - 1.0.10"

    def test_base_input_filter(self) -> None:
        technology = Technology(name="Apache")
        self.assertTrue(technology.filter(Input(filter="apache")))
        self.assertTrue(technology.filter(Input(filter="pach")))
        self.assertTrue(technology.filter(Input(filter="APACHE")))
        self.assertFalse(technology.filter(Input(filter="nginx")))
        # OR
        self.assertTrue(technology.filter(Input(filter="nginx or apache")))
        # AND
        self.assertTrue(technology.filter(Input(filter="!nginx and !akamai")))
        # Negation
        self.assertTrue(technology.filter(Input(filter="!nginx")))
        self.assertFalse(technology.filter(Input(filter="!apache")))
        # Empty filter
        self.assertTrue(technology.filter(Input(filter="")))

    def test_deduplication(self):
        first = Technology.objects.create_finding(self.execution, port=self.port, name="Grafana", version="10.1.0")
        second = Technology.objects.create_finding(self.execution, port=self.port, name="Grafana")
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, Technology.objects.filter(port=self.port, name="Grafana").count())
        self.assertEqual("10.1.0", second.version)
        self.assertNotEqual(
            second.id,
            Technology.objects.create_finding(self.execution, port=self.port, name="Grafana", version="10.2.0").id,
        )

    def test_deduplication_with_user_input(self):
        user_finding = Technology.objects.create_finding(
            self.execution, port=self.port, name="Joomla", created_from_user_input=True
        )
        detected_finding = Technology.objects.create_finding(
            self.execution,
            port=self.port,
            name="Joomla",
            version="4.2.0",
            created_from_user_input=False,
        )
        self.assertEqual(user_finding.id, detected_finding.id)
        self.assertEqual(1, Technology.objects.filter(port=self.port, name="Joomla").count())
        self.assertEqual("4.2.0", detected_finding.version)
        self.assertFalse(detected_finding.created_from_user_input)

    def test_deduplication_with_new_user_input(self):
        detected_finding = Technology.objects.create_finding(
            self.execution, port=self.port, name="Drupal", version="9.5.0"
        )
        user_finding = Technology.objects.create_finding(
            self.execution, port=self.port, name="Drupal", created_from_user_input=True
        )
        self.assertEqual(detected_finding.id, user_finding.id)
        self.assertEqual(1, Technology.objects.filter(port=self.port, name="Drupal").count())
        self.assertEqual("9.5.0", user_finding.version)
        self.assertFalse(user_finding.created_from_user_input)
