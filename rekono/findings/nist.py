import requests
from findings.enums import Severity

CVSS_RANGES = {
    Severity.CRITICAL: (9, 10),
    Severity.HIGH: (7, 9),
    Severity.MEDIUM: (4, 7),
    Severity.LOW: (2, 4),
    Severity.INFO: (0, 2)
}


def get_description(data: dict) -> str:
    options = data.get('cve').get('description').get('description_data')
    for o in options:
        if o.get('lang') == 'en':
            return o.get('value')
    return ''


def get_cwe(data: dict) -> str:
    items = data.get('cve').get('problemtype').get('problemtype_data')
    for item in items:
        descriptions = item.get('description')
        if descriptions:
            for desc in descriptions:
                cwe = desc.get('value')
                if not cwe:
                    continue
                if cwe.lower().startswith('cwe-'):
                    return cwe
    return None


def get_severity(data: dict) -> str:
    cvss = data.get('impact')
    score = 5
    if 'baseMetricV3' in cvss:
        score = cvss.get('baseMetricV3').get('cvssV3').get('baseScore')
    elif 'baseMetricV2' in cvss:
        score = cvss.get('baseMetricV2').get('cvssV2').get('baseScore')
    for severity in CVSS_RANGES.keys():
        down, up = CVSS_RANGES[severity]
        if (
            (score >= down and score < up)
            or (severity == Severity.CRITICAL and score >= down and score <= up)
        ):
            return severity
    return None


def get_cve_information(cve: str) -> dict:
    res = requests.get('https://services.nvd.nist.gov/rest/json/cve/1.0/{cve}'.format(cve=cve))
    if res.status_code == 200:
        data = res.json().get('result').get('CVE_Items')[0]
        return {
            'description': get_description(data),
            'severity': get_severity(data),
            'cwe': get_cwe(data),
            'reference': 'https://nvd.nist.gov/vuln/detail/{cve}'.format(cve=cve)
        }
    return {}
