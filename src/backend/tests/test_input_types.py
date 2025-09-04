from functools import cached_property

from input_types.models import InputType
from tests.framework import ApiTest

# pytype: disable=wrong-arg-types


class InputTypeTest(ApiTest):
    expected_string = "OSINT"

    @cached_property
    def object(self) -> InputType:
        return InputType.objects.get(pk=1)
