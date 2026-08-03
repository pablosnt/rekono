from functools import cached_property
from unittest.mock import patch

from django.test import TestCase

from executions.models import Execution
from findings.models import Host
from security.authorization.roles import Role
from targets.enums import TargetType
from targets.models import Target
from tasks.models import Task
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase
from tests.framework.data import SetupProject
from tools.models import Input

# pytype: disable=wrong-arg-types

target1 = {"project": 1, "target": "10.10.10.10"}
target2 = {"project": 1, "target": "scanme.nmap.org"}
target3 = {"project": 1, "target": "10.10.10.1-24"}
target4 = {"project": 1, "target": "10.10.10.0/24"}
target5 = {"project": 1, "target": "8.8.8.8"}
invalid_target = {"project": 1, "target": "domain-not-found"}
# IP ranges accepted by the IP range pattern that can't be expanded into addresses
invalid_ip_range = {"project": 1, "target": "10.10.10.1-999"}
reversed_ip_range = {"project": 1, "target": "10.10.10.50-1"}


class TargetTest(ApiTest, TestCase):
    endpoint = "/api/targets/"
    expected_string = target1.get("target")
    data = [SetupProject(targets_and_tasks=0)]
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        PostApiTestCase(["admin2", "auditor2", "reader1", "reader2"], 403, target1),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_target),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_ip_range),
        PostApiTestCase(["admin1", "auditor1"], 400, reversed_ip_range),
        PostApiTestCase(["admin1"], data=target1, expected={"id": 1, "type": TargetType.PRIVATE_IP, **target1}),
        PostApiTestCase(["auditor1"], data=target2, expected={"id": 2, "type": TargetType.DOMAIN, **target2}),
        PostApiTestCase(["auditor1"], data=target3, expected={"id": 3, "type": TargetType.IP_RANGE, **target3}),
        PostApiTestCase(["admin1"], data=target4, expected={"id": 4, "type": TargetType.NETWORK, **target4}),
        PostApiTestCase(["auditor1"], data=target5, expected={"id": 5, "type": TargetType.PUBLIC_IP, **target5}),
        PostApiTestCase(["admin1", "auditor1"], 400, target1),
        ApiTestCase(
            ["members"],
            expected=[
                {"id": 5, "type": TargetType.PUBLIC_IP, **target5},
                {"id": 4, "type": TargetType.NETWORK, **target4},
                {"id": 3, "type": TargetType.IP_RANGE, **target3},
                {"id": 2, "type": TargetType.DOMAIN, **target2},
                {"id": 1, "type": TargetType.PRIVATE_IP, **target1},
            ],
        ),
        ApiTestCase(["members"], expected={"id": 2, "type": TargetType.DOMAIN, **target2}, endpoint="2"),
        ApiTestCase(["not_members"]),
        ApiTestCase(["not_members"], 404, endpoint="1"),
        DeleteApiTestCase(["reader1", "reader2"], 403, endpoint="1"),
        DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="1"),
        DeleteApiTestCase(["auditor1"], endpoint="1"),
        DeleteApiTestCase(["admin1"], 404, endpoint="1"),
        DeleteApiTestCase(["admin1"], endpoint="2"),
        DeleteApiTestCase(["auditor1"], endpoint="3"),
        DeleteApiTestCase(["admin1"], endpoint="4"),
        DeleteApiTestCase(["auditor1"], endpoint="5"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
    ]

    def test_base_input_filter(self) -> None:
        target = Target(type=TargetType.DOMAIN)
        self.assertTrue(target.filter(Input(filter="domain")))
        self.assertFalse(target.filter(Input(filter="private_ip")))
        # OR
        self.assertTrue(target.filter(Input(filter="domain or private_ip")))
        # Negation
        self.assertTrue(target.filter(Input(filter="!private_ip")))
        self.assertFalse(target.filter(Input(filter="!domain")))
        # Not applicable
        self.assertTrue(target.filter(Input(filter="anything")))
        # Empty filter
        self.assertTrue(target.filter(Input(filter="")))

    @cached_property
    def object(self) -> Target:
        return Target(**{**target1, "project": self.project})

    def test_resolve_domain_cache_hit(self) -> None:
        ip = "9.9.9.9"
        with patch.object(Target._dns_cache, "get", return_value=ip):
            self.assertEqual(ip, Target.resolve_domain("cached.example.com"))

    def test_create_finding_from_user_input(self) -> None:
        ip, domain = "1.2.3.4", "example.com"
        domain_target = Target.objects.create(project=self.project, target=domain, type=TargetType.DOMAIN)
        execution = Execution.objects.create(
            task=Task.objects.create(target=domain_target, configuration=self.configuration),
            configuration=self.configuration,
        )
        with patch.object(Target, "resolve_domain", return_value=ip):
            host = domain_target.create_finding_from_user_input(execution)
        self.assertIsInstance(host, Host)
        self.assertEqual(ip, host.ip)
        self.assertEqual(domain, host.domain)
        # Unresolvable domain -> No finding
        with patch.object(Target, "resolve_domain", return_value=None):
            self.assertIsNone(domain_target.create_finding_from_user_input(execution))
        # Non-IP and non-domain target -> No finding
        self.assertIsNone(
            Target.objects.create(
                project=self.project, target="10.10.10.0/24", type=TargetType.NETWORK
            ).create_finding_from_user_input(execution)
        )
