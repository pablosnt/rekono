

from typing import Any


class BaseInput:

    def filter(self, input: Any) -> bool:
        return True

    def parse(self, accumulated: dict = {}) -> dict:
        return {}
