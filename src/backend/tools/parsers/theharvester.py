"""TheHarvester OSINT reconnaissance tool output parser.

Processes TheHarvester JSON output to extract open source intelligence
findings including emails, domains, IPs, and social media information.
"""

from findings.enums import OSINTDataType
from findings.models import OSINT
from tools.parsers.base import BaseParser


class Theharvester(BaseParser):
    """Parser for TheHarvester JSON output files.

    Extracts OSINT findings from passive reconnaissance data including email
    addresses, domains, IP addresses, social media profiles, and ASN information.
    Maps TheHarvester data types to standardized OSINT finding categories.

    Attributes:
        data_types (dict): Mapping between TheHarvester types and OSINT data types
    """

    # Mapping between theHarvester types and OSINT data types
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
        """Parse TheHarvester JSON output and extract OSINT findings.

        Processes JSON reconnaissance data to create OSINT findings for
        discovered intelligence across multiple data sources.
        """
        data = self.load_json_report()
        if not data or not isinstance(data, dict):
            return
        for the_harvester_type, items in data.items():
            for item in items:
                if the_harvester_type in self.data_types:
                    self.create_finding(OSINT, data=item, data_type=self.data_types[the_harvester_type])
