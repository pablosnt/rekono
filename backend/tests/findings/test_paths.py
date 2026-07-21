from django.test import TestCase

from findings.enums import PathType, TransportProtocol
from findings.models import Path
from tests.findings.base import FindingTest
from tools.models import Input

# pytype: disable=wrong-arg-types,attribute-error


class PathTest(FindingTest, TestCase):
    model = Path
    endpoint = "/api/paths/"
    expected_defectdojo = None
    expected_string = f"10.10.10.10 - 80 - {TransportProtocol.TCP.value} - /index.html"

    def test_base_input_filter(self) -> None:
        path = Path(path="/admin/login", status=200, type=PathType.ENDPOINT)
        # By path
        self.assertTrue(path.filter(Input(filter="admin")))
        self.assertTrue(path.filter(Input(filter="/ADMIN/LOGIN")))
        self.assertFalse(path.filter(Input(filter="secret")))
        # By status
        self.assertTrue(path.filter(Input(filter="200")))
        self.assertFalse(path.filter(Input(filter="404")))
        # By type
        self.assertTrue(path.filter(Input(filter="endpoint")))
        self.assertFalse(path.filter(Input(filter="share")))
        # AND
        self.assertTrue(path.filter(Input(filter="admin and 200")))
        self.assertFalse(path.filter(Input(filter="admin and 404")))
        # OR
        self.assertTrue(path.filter(Input(filter="secret or endpoint")))
        # Negation
        self.assertTrue(path.filter(Input(filter="!404")))
        self.assertFalse(path.filter(Input(filter="!200")))
        # Empty filter
        self.assertTrue(path.filter(Input(filter="")))

    def test_defectdojo(self):
        defectdojo_endpoint = {"protocol": "http", "host": "10.10.10.10", "port": 80, "path": "/index.html"}
        parsed = self.path.defectdojo_endpoint()
        for key, value in defectdojo_endpoint.items():
            self.assertEqual(value, parsed[key])

    def test_deduplication(self):
        first = Path.objects.create_finding(self.execution, port=self.port, path="/admin", status=403)
        second = Path.objects.create_finding(self.execution, port=self.port, path="/admin")
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, Path.objects.filter(port=self.port, path="/admin").count())
        self.assertEqual(403, second.status)
        self.assertNotEqual(second.id, Path.objects.create_finding(self.execution, port=self.port, path="/login").id)
