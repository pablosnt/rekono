from django.test import TestCase

from findings.enums import PortStatus, Severity, TransportProtocol
from findings.models import Port
from tests.findings.base import FindingTest

# pytype: disable=wrong-arg-types,attribute-error


class PortTest(FindingTest, TestCase):
    model = Port
    endpoint = "/api/ports/"
    expected_defectdojo = {
        "title": "Port discovered",
        "description": f"Host: 10.10.10.10\nPort: 80\nStatus: {PortStatus.OPEN.value}\nProtocol: {TransportProtocol.TCP.value}\nService: http",
        "severity": str(Severity.INFO),
    }
    expected_string = f"10.10.10.10 - 80 - {TransportProtocol.TCP.value}"

    def test_deduplication(self):
        first = Port.objects.create_finding(
            self.execution, host=self.host, port=8443, protocol=TransportProtocol.TCP, service="https-alt"
        )
        second = Port.objects.create_finding(self.execution, host=self.host, port=8443)
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, Port.objects.filter(host=self.host, port=8443).count())
        self.assertEqual(TransportProtocol.TCP, second.protocol)
        self.assertNotEqual(
            second.id,
            Port.objects.create_finding(
                self.execution, host=self.host, port=8443, protocol=TransportProtocol.UDP, service="unknown"
            ).id,
        )

    def test_deduplication_with_user_input(self):
        user_finding = Port.objects.create_finding(
            self.execution, host=self.host, port=8080, created_from_user_input=True
        )
        detected_finding = Port.objects.create_finding(
            self.execution,
            host=self.host,
            port=8080,
            protocol=TransportProtocol.TCP,
            service="http-alt",
            created_from_user_input=False,
        )
        self.assertEqual(user_finding.id, detected_finding.id)
        self.assertEqual(1, Port.objects.filter(host=self.host, port=8080).count())
        self.assertEqual(TransportProtocol.TCP, detected_finding.protocol)
        self.assertEqual("http-alt", detected_finding.service)
        self.assertFalse(detected_finding.created_from_user_input)

    def test_deduplication_with_new_user_input(self):
        detected_finding = Port.objects.create_finding(
            self.execution, host=self.host, port=9090, protocol=TransportProtocol.TCP, service="websocket"
        )
        user_finding = Port.objects.create_finding(
            self.execution, host=self.host, port=9090, created_from_user_input=True
        )
        self.assertEqual(detected_finding.id, user_finding.id)
        self.assertEqual(1, Port.objects.filter(host=self.host, port=9090).count())
        self.assertEqual(TransportProtocol.TCP, user_finding.protocol)
        self.assertEqual("websocket", user_finding.service)
        self.assertFalse(user_finding.created_from_user_input)
