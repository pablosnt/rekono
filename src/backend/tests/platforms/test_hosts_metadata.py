from tests.framework import RekonoTest
from platforms.hosts_metadata import HostsMetadata


class HostsMetadataTest(RekonoTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
        self._setup_findings(self.execution1)

    def _test_integration(self, expected: list[tuple[str, str | None]]) -> None:
        client = HostsMetadata()
        client.process_findings(self.execution1, [self.host])
        for field, value in expected:
            self.assertEqual(getattr(self.host, field), value)

    def test_public_ip(self) -> None:
        self.host.ip = "8.8.8.8"
        self._test_integration(
            [
                ("domain", "dns.google"),
                ("country", "US"),
                ("city", "Mountain View"),
            ]
        )

    def test_unresolvable_private_ip(self) -> None:
        self._test_integration([("domain", None), ("country", None), ("city", None)])
