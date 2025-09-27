from functools import cached_property
from typing import Any, Callable

from executions.models import Execution
from findings.models import Host
from framework.platforms import BaseIntegration
from platforms.virustotal.models import VirusTotalSettings
from targets.enums import TargetType
from targets.models import Target


class VirusTotal(BaseIntegration):
    finding_types = [Host]
    url = "https://www.virustotal.com/api/v3/"

    @cached_property
    def settings(self) -> VirusTotalSettings:
        return VirusTotalSettings.objects.first()

    def is_available(self) -> bool:
        if self.settings.secret is None:
            return False
        try:
            self._request(self.session.get, "ip_addresses/8.8.8.8")
            return True
        except Exception:
            return False

    # TODO: Test the integration manually
    # TODO: Docstrings
    def _request(self, method: Callable, url: str, json: bool = True, trigger_exception: bool = True, **kwargs: Any):
        return super()._request(
            method,
            f"{self.url}{url}",
            json,
            trigger_exception,
            **{**kwargs, "headers": {"accept": "application/json", "x-apikey": self.settings.secret}},
        )

    def is_finding_processable(self, finding: Host) -> bool:
        return super().is_finding_processable(finding) and (
            finding.domain is not None or Target.get_type(finding.ip) is TargetType.PUBLIC_IP
        )

    def _process_finding(self, execution: Execution, finding: Host) -> None:
        try:
            if finding.domain is not None:
                data = self._request(self.session.get, f"domains/{finding.domain}")
            elif finding.ip is not None:
                data = self._request(self.session.get, f"ip_addresses/{finding.ip}")
            else:
                return
            data = data.get("data", {}).get("attributes", {})
            finding.reputation = data.get("reputation")
            finding.harmless_votes = data.get("total_votes", {}).get("harmless")
            finding.malicious_votes = data.get("total_votes", {}).get("malicious")
            finding.whois = data.get("whois")
            finding.save(update_fields=["reputation", "harmless_votes", "malicious_votes", "whois"])
        except Exception:
            pass
