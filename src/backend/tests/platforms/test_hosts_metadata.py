from platforms.hosts_metadata import HostsMetadata
from tests.framework import BaseTest


class HostsMetadataTest(BaseTest):
    setup_entities = ["findings"]

    def setUp(self) -> None:
        super().setUp()
        self.client = HostsMetadata()

    def test_public_ip(self) -> None:
        self.host.ip = "8.8.8.8"
        self.client.process_finding(self.selected_execution, self.host)
        for field, value in {"domain": "dns.google", "country": "US", "city": "Mountain View"}.items():
            self.assertEqual(value, getattr(self.host, field))

    def test_unresolvable_private_ip(self) -> None:
        self.client.process_finding(self.selected_execution, self.host)
        for field in ["domain", "country", "city"]:
            self.assertIsNone(getattr(self.host, field))
