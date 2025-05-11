import socket

import geocoder

from findings.models import Host
from framework.platforms import BaseIntegration
from targets.enums import TargetType
from targets.models import Target


class HostsMetadata(BaseIntegration):
    def __init__(self):
        pass

    def is_enabled(self) -> bool:
        return True

    def _process_findings(self, execution, findings):
        for finding in findings:
            if isinstance(finding, Host):
                ip_type = Target.get_type(finding.ip)
                if finding.domain is None and ip_type in [
                    TargetType.PRIVATE_IP,
                    TargetType.PUBLIC_IP,
                ]:
                    try:
                        finding.domain = socket.gethostbyaddr(finding.ip)[0]
                    except Exception:  # nosec
                        pass
                if ip_type == TargetType.PUBLIC_IP and not all(
                    [finding.country, finding.city, finding.latitude, finding.longitude]
                ):
                    geocode = geocoder.ip(finding.ip)
                    if geocode and geocode.ok:
                        finding.country = geocode.country
                        finding.city = geocode.city
                        finding.latitude, finding.longitude = geocode.latlng
                finding.save(update_fields=["domain", "country", "city", "latitude", "longitude"])
