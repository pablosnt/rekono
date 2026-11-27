import socket
from unittest import mock

from django.test import TestCase

from platforms.hosts_metadata import HostsMetadata
from tests.framework import BaseTest
from tests.framework.data import SetupProject

_reverse_dns = mock.Mock(return_value=("dns.google", [], ["8.8.8.8"]))
_unresolvable = mock.Mock(side_effect=socket.herror)
_geolocation = mock.Mock(return_value=mock.Mock(ok=True, country="US", city="Mountain View", latlng=[37.4, -122.0]))
_no_geolocation = mock.Mock(return_value=mock.Mock(ok=False))


class HostsMetadataTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self) -> None:
        super().setUp()
        self.client = HostsMetadata()

    def _test(self, expected: dict[str, object]) -> None:
        self.client.process_finding(self.execution, self.host)
        for field, value in expected.items():
            self.assertEqual(value, getattr(self.host, field))

    @mock.patch("platforms.hosts_metadata.socket.gethostbyaddr", _reverse_dns)
    @mock.patch("platforms.hosts_metadata.geocoder.ip", _geolocation)
    def test_public_ip(self) -> None:
        self.host.ip = "8.8.8.8"
        self._test(
            {"domain": "dns.google", "country": "US", "city": "Mountain View", "latitude": 37.4, "longitude": -122.0}
        )

    @mock.patch("platforms.hosts_metadata.socket.gethostbyaddr", _unresolvable)
    @mock.patch("platforms.hosts_metadata.geocoder.ip", _no_geolocation)
    def test_unresolvable_public_ip(self) -> None:
        self.host.ip = "8.8.8.8"
        self._test({"domain": None, "country": None, "city": None})

    @mock.patch("platforms.hosts_metadata.socket.gethostbyaddr", _unresolvable)
    @mock.patch("platforms.hosts_metadata.geocoder.ip")
    def test_unresolvable_private_ip(self, geolocation: mock.Mock) -> None:
        self.host.ip = "10.10.10.10"
        self._test({"domain": None, "country": None, "city": None})
        geolocation.assert_not_called()
