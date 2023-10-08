from findings.enums import OSINTDataType
from findings.models import OSINT
from tools.parsers.base import BaseParser


class Theharvester(BaseParser):
    # Mapping between theHarvester types and OSINT data types
    data_types = {
        "ips": OSINTDataType.IP,
        "hosts": OSINTDataType.DOMAIN,
        "vhosts": OSINTDataType.VHOST,
        "urls": OSINTDataType.URL,
        "trello_urls": OSINTDataType.URL,
        "interesting_urls": OSINTDataType.URL,
        "emails": OSINTDataType.EMAIL,
        "linkedin_links": OSINTDataType.LINK,
        "asns": OSINTDataType.ASN,
        "twitter_people": OSINTDataType.USER,
        "linkedin_people": OSINTDataType.USER,
    }

    def _parse_report(self) -> None:
        data = self._load_report_as_json()
        for the_harvester_type, items in data.items():
            for item in items:
                self.create_finding(
                    OSINT, data=item, data_type=self.data_types[the_harvester_type]
                )
