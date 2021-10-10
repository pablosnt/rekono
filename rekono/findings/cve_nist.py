import requests
from findings.models import Vulnerability
from findings.enums import Severity


CVSS_RANGES = {
    Severity.CRITICAL: (9, 10),
    Severity.HIGH: (7, 9),
    Severity.MEDIUM: (4, 7),
    Severity.LOW: (2, 4),
    Severity.INFO: (0, 2)
}


def get_description(data: str) -> str:
    options = data.get('cve').get('description').get('description_data')
    for o in options:
        if o.get('lang') == 'en':
            return o.get('value')
    return ''


def get_severity(data: str) -> Severity:
    cvss = data.get('impact')
    score = 5
    if 'baseMetricV3' in cvss:
        score = cvss.get('baseMetricV3').get('cvssV3').get('baseScore')
    elif 'baseMetricV2' in cvss:
        score = cvss.get('baseMetricV2').get('cvssV2').get('baseScore')
    for severity in CVSS_RANGES.keys():
        down, up = CVSS_RANGES[severity]
        if score >= down and score < up:
            return severity
        if severity == Severity.CRITICAL and score >= down and score <= up:
            return severity


def get_information(cve: str) -> dict:
    res = requests.get('https://services.nvd.nist.gov/rest/json/cve/1.0/{cve}'.format(cve=cve))
    if res.status_code == 200:
        data = res.json().get('result').get('CVE_Items')[0]
        return {
            'description': get_description(data),
            'severity': get_severity(data),
            'reference': 'https://nvd.nist.gov/vuln/detail/{cve}'.format(cve=cve)
        }
    return {}
