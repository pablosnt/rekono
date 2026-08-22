"""Things that an alert can watch."""

from django.db.models import TextChoices
from django.db.models.enums import Choices


class AlertItem(TextChoices):
    """Kind of finding that triggers an alert when it's discovered.

    Some items watch the same finding type with a different condition, like the
    open ports and the services, or the CVEs and the ones that are trending.
    """

    OSINT = "OSINT"
    HOST = "Host"
    OPEN_PORT = "Open Port"
    SERVICE = "Service"
    TECHNOLOGY = "Technology"
    CREDENTIAL = "Credential"
    VULNERABILITY = "Vulnerability"
    CVE = "CVE"
    TRENDING_CVE = "Trending CVE"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
AlertItem: type[Choices] = AlertItem
