from django.test import TestCase

from findings.models import Exploit, Host, Port, Vulnerability
from parameters.models import InputTechnology, InputVulnerability
from target_ports.models import TargetPort
from targets.models import Target
from tests.framework import ParserTest


class BaseParserTest(ParserTest, TestCase):
    tool_name = "Nmap"
    target_parameters_flag = True

    def setUp(self):
        super().setUp()
        self.executor = self.tool.executor_class(self.execution)

    def test_create_finding_unlinked(self):
        parser = self.tool.parser_class(self.executor, "")
        finding = parser.create_finding(Port, port=80)
        # finding is created without a host link because we are in a unit test
        self.assertIsNone(finding.host)

    def test_create_finding_linked_to_previous_finding(self):
        parser = self.tool.parser_class(self.executor, "")
        host = Host.objects.create(ip="10.10.10.10")
        self.executor.findings_used_in_execution = {Host: host}
        finding = parser.create_finding(Port, port=80)
        self.assertEqual(host, finding.host)

    def test_create_finding_linked_to_targets(self):
        parser = self.tool.parser_class(self.executor, "")
        self.executor.findings_used_in_execution = {}
        self.executor.targets_used_in_execution = {TargetPort: self.targetport, Target: self.target}
        finding = parser.create_finding(Port, port=80)
        self.assertEqual(self.target.target, finding.host.ip)
        finding = parser.create_finding(Vulnerability, name="Test", cve="2025-1111-2222")
        self.assertEqual(self.target.target, finding.port.host.ip)
        self.assertEqual(self.targetport.port, finding.port.port)

    def test_create_finding_linked_to_input_parameters(self):
        parser = self.tool.parser_class(self.executor, "")
        self.executor.targets_used_in_execution = {
            TargetPort: self.targetport,
            InputVulnerability: self.input_vulnerability,
        }
        self.executor.scanned_port = self.targetport
        finding = parser.create_finding(Exploit, title="Test")
        self.assertEqual(self.input_vulnerability.cve, finding.vulnerability.cve)
        self.assertEqual(self.targetport.port, finding.vulnerability.port.port)
        self.assertEqual(self.target.target, finding.vulnerability.port.host.ip)
        other_target_port = TargetPort.objects.create(target=self.target, port=8080, path=None)
        self.executor.targets_used_in_execution = {
            TargetPort: other_target_port,
            InputTechnology: self.input_technology,
        }
        finding = parser.create_finding(Exploit, title="Test")
        self.assertEqual(self.input_technology.name, finding.technology.name)
        self.assertEqual(other_target_port.port, finding.technology.port.port)
        self.assertEqual(self.target.target, finding.technology.port.host.ip)
