from tests.framework import RekonoTest
from platforms.hosts_metadata import HostsMetadata


class HostsMetadataTest(RekonoTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
        self._setup_findings(self.execution1)
        self.host.ip = "8.8.8.8"
        self.host.save(update_fields=["ip"])

    def test_integration(self) -> None:
        client = HostsMetadata()
        client.process_findings(self.execution1, [self.host])
        for field, expected in [
            ("domain", "dns.google"),
            ("country", "US"),
            ("city", "Mountain View"),
        ]:
            self.assertEqual(getattr(self.host, field), expected)
