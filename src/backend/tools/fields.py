from framework.fields import IntegerChoicesField


class StageField(IntegerChoicesField):
    def to_representation(self, value: int) -> str:
        representation = super().to_representation(value)
        if value == 1:
            representation = representation.upper()
        return representation
