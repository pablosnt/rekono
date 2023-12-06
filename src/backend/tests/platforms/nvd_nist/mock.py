from typing import Any, Dict

success = {
    "result": {
        "CVE_Items": [
            {
                "cve": {
                    "description": {
                        "description_data": [{"lang": "en", "value": "description"}]
                    },
                    "problemtype": {
                        "problemtype_data": [{"description": [{"value": "CWE-200"}]}]
                    },
                }
            }
        ]
    }
}


def _success(impact_value: Dict[str, Any]) -> Dict[str, Any]:
    success["result"]["CVE_Items"][0]["impact"] = impact_value
    return success


def success_cvss_3(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    return _success(
        {
            "baseMetricV3": {"cvssV3": {"baseScore": 9}},
        }
    )


def success_cvss_2(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    return _success(
        {
            "baseMetricV2": {"cvssV2": {"baseScore": 8}},
        }
    )


def not_found(*args: Any, **kwargs: Any) -> dict:
    raise Exception("CVE not found")
