from typing import Any

'''Mock for NVD NIST API integration implemented on findings.nvd_nist package.'''


nvd_nist_base_success = {                                                       # NVD NIST base Response
    'cve': {
        'description': {
            'description_data': [
                {
                    'lang': 'en',
                    'value': 'description'
                }
            ]
        },
        'problemtype': {
            'problemtype_data': [
                {
                    'description': [
                        {
                            'value': 'CWE-200'
                        }
                    ]
                }
            ]
        }
    },
    'impact': {}
}


def nvd_nist_success_cvss_3(*args: Any, **kwargs: Any) -> dict:
    '''Get mocked response from CVE with CVSS 3.

    Returns:
        dict: NVD NIST response
    '''
    response = nvd_nist_base_success.copy()
    response['impact'] = {
        'baseMetricV3': {
            'cvssV3': {
                'baseScore': 9
            }
        }
    }
    return response


def nvd_nist_success_cvss_2(*args: Any, **kwargs: Any) -> dict:
    '''Get mocked response from CVE with CVSS 2.

    Returns:
        dict: NVD NIST response
    '''
    response = nvd_nist_base_success.copy()
    response['impact'] = {
        'baseMetricV2': {
            'cvssV2': {
                'baseScore': 8
            }
        }
    }
    return response


def nvd_nist_not_found(*args: Any, **kwargs: Any) -> dict:
    '''Get mocked response from not found CVE

    Returns:
        dict: Empty response
    '''
    return {}
