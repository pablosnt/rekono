from typing import Any

'''Mock for NVD NIST API integration implemented on findings.nvd_nist package.'''


nvd_nist_base_success = {                                                       # NVD NIST base Response
    "vulnerabilities": [
        {
            "cve": {
                "descriptions": [{"lang": "en", "value": "description"}],
                "weaknesses": [
                    {
                        "type": "Primary",
                        "description": [{"lang": "en", "value": "CWE-200"}],
                    },
                    {
                        "type": "Secondary",
                        "description": [{"lang": "en", "value": "CWE-300"}],
                    },
                ],
                "metrics": {},
            }
        }
    ]
}


def nvd_nist_success_cvss_3(*args: Any, **kwargs: Any) -> dict:
    '''Get mocked response from CVE with CVSS 3.

    Returns:
        dict: NVD NIST response
    '''
    response = nvd_nist_base_success.copy()
    response['vulnerabilities'][0]["cve"]["metrics"] = {
        "cvssMetricV31": [{"type": "Primary", "cvssData": {"baseScore": 9}}]
    }
    return response.get("vulnerabilities")[0].get("cve", {})


def nvd_nist_success_cvss_2(*args: Any, **kwargs: Any) -> dict:
    '''Get mocked response from CVE with CVSS 2.

    Returns:
        dict: NVD NIST response
    '''
    response = nvd_nist_base_success.copy()
    response['vulnerabilities'][0]["cve"]["metrics"] = {
        "cvssMetricV2": [{"type": "Primary", "cvssData": {"baseScore": 8}}]
    }
    return response.get("vulnerabilities")[0].get("cve", {})


def nvd_nist_not_found(*args: Any, **kwargs: Any) -> dict:
    '''Get mocked response from not found CVE

    Returns:
        dict: Empty response
    '''
    return {}
