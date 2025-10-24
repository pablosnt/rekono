from functools import cached_property

from django.test import TestCase

from input_types.models import InputType
from tests.framework import ApiTestNoData

# pytype: disable=wrong-arg-types


class InputTypeTest(ApiTestNoData, TestCase):
    expected_string = "OSINT"

    @cached_property
    def object(self) -> InputType:
        return InputType.objects.get(pk=1)
