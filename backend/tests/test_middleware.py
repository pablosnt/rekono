from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase, override_settings
from rest_framework.throttling import BaseThrottle

# pytype: disable=wrong-arg-types

TRUSTED_PROXIES = {**settings.REST_FRAMEWORK, "NUM_PROXIES": 1}


class MiddlewareTest(TestCase):
    remote_source_ip = "10.0.0.1"
    nginx_source_ip = "203.0.113.9"
    tampered_source_ip = "1.2.3.4"

    def _source_ip(self, x_forwarded_for: str | None = None) -> str:
        request = HttpRequest()
        request.META["REMOTE_ADDR"] = self.remote_source_ip
        if x_forwarded_for is not None:
            request.META["HTTP_X_FORWARDED_FOR"] = x_forwarded_for
        return BaseThrottle().get_ident(request)

    def test_remote_addr_used_without_trusted_proxies(self) -> None:
        # Without a trusted proxy the client-supplied header is ignored
        self.assertEqual(self.remote_source_ip, self._source_ip(f"{self.tampered_source_ip}, {self.nginx_source_ip}"))

    @override_settings(REST_FRAMEWORK=TRUSTED_PROXIES)
    def test_rightmost_value_used_with_trusted_proxies(self) -> None:
        # nginx appends the real client IP on the right, so the spoofed leftmost value is ignored
        self.assertEqual(self.nginx_source_ip, self._source_ip(f"{self.tampered_source_ip}, {self.nginx_source_ip}"))
        # A single (real) value is returned as-is, trimmed
        self.assertEqual(self.nginx_source_ip, self._source_ip(f" {self.nginx_source_ip} "))

    @override_settings(REST_FRAMEWORK=TRUSTED_PROXIES)
    def test_remote_addr_used_when_header_absent(self) -> None:   # trufflehog:ignore
        self.assertEqual(self.remote_source_ip, self._source_ip())
