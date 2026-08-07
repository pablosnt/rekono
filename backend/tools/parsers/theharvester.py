"""Parser of theHarvester OSINT tool."""

from findings.enums import OSINTDataType
from findings.models import OSINT
from tools.parsers.base import BaseParser


class Theharvester(BaseParser):
    """Findings discovered by theHarvester, read from its JSON report.

    Attributes:
        data_types: Kind of data that theHarvester reports under each key of its
          report, without the ones that Rekono can't store, like the Shodan data.
    """

    data_types = {
        "ips": OSINTDataType.IP,
        "hosts": OSINTDataType.DOMAIN,
        "vhosts": OSINTDataType.VHOST,
        "urls": OSINTDataType.URL,
        "trello_urls": OSINTDataType.URL,
        "interesting_urls": OSINTDataType.URL,
        "emails": OSINTDataType.EMAIL,
        "linkedin_links": OSINTDataType.URL,
        "asns": OSINTDataType.ASN,
        "twitter_people": OSINTDataType.USER,
        "linkedin_people": OSINTDataType.USER,
    }

    def _parse(self) -> None:
        """Create one OSINT finding per piece of data found in the report."""
        data = self.load_json_report()
        if not data or not isinstance(data, dict):
            return
        for the_harvester_type, items in data.items():
            for item in items:
                if the_harvester_type in self.data_types:
                    self.create_finding(OSINT, data=item, data_type=self.data_types[the_harvester_type])
