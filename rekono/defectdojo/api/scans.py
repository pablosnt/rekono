import requests
from rekono.settings import DEFECT_DOJO as config
from tools.models import Tool
from executions.models import Execution
from defectdojo.api import utils


def import_scan(engagement: int, execution: Execution, tool: Tool) -> None:
    data = {
        'scan_type': tool.defectdojo_scan_type,
        'engagement': engagement,
        'tags': config.get('REKONO_TAGS'),
    }
    files = {
        'file': open(execution.output_file, 'r'),
    }
    requests.post(utils.urls.get('import'), headers=utils.headers, files=files, data=data)
