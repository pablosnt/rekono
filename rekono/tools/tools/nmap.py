import os

from executions.models import Execution
from libnmap.parser import NmapParser
from findings.models import Enumeration, Host, Technology
from tools.tools.base_tool import BaseTool


class NmapTool(BaseTool):

    file_output_enabled = True

    def parse_output(self, output: str) -> list:
        findings = []
        full_path = os.path.join(self.directory_output, self.filename_output)
        if os.path.isfile(full_path):
            report = NmapParser.parse_fromfile(full_path)
            for h in report.hosts:
                if not h.is_up():
                    continue
                os_detections = h.os_match_probabilities()
                os_text = None
                os_type = None
                if os_detections:
                    selected_os = None
                    accuracy = 0
                    for o in os_detections:
                        if o.accuracy > accuracy:
                            selected_os = o
                            os_text = o.name
                    accuracy = 0
                    for c in selected_os.osclasses:
                        if c.accuracy > accuracy:
                            try:
                                os_type = Host.OSType[c.osfamily.upper()]
                            except KeyError:
                                os_type = Host.OSType.OTHER
                host = Host.objects.create(
                    address=h.address,
                    os=os_text,
                    os_type=os_type
                )
                findings.append(host)
                for s in h.services:
                    enumeration = Enumeration.objects.create(
                        host=host,
                        port=s.port,
                        port_status=Enumeration.PortStatus[s.state.upper()],
                        protocol=Enumeration.Protocol[s.protocol.upper()],
                        service=s.service
                    )
                    findings.append(enumeration)
                    if 'product' in s.service_dict and 'version' in s.service_dict:
                        technology = Technology.objects.create(
                            enumeration=enumeration,
                            name=s.service_dict.get('product'),
                            version=s.service_dict.get('version')
                        )
                        findings.append(technology)
        return findings
