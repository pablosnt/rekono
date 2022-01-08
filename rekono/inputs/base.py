from tools.models import Input


class BaseInput:

    def filter(self, input: Input) -> bool:
        return True

    def parse(self, accumulated: dict = {}) -> dict:
        return {}
