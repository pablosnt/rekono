from executions.enums import ParameterKey


def check_parameter(parameter) -> None:
    checkers = {
        ParameterKey.TECHNOLOGY: '',
        ParameterKey.VERSION: '',
        ParameterKey.HTTP_ENDPOINT: '',
        ParameterKey.CVE: '',
        ParameterKey.EXPLOIT: ''
    }
    checkers[parameter.key]
