from typing import Any

from input_types.models import InputType
from tests.framework import ApiTest


class InputTypeTest(ApiTest):
    expected_str = "OSINT"

    def _get_object(self) -> Any:
        return InputType.objects.get(pk=1)
