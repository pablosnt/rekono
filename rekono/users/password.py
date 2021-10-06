from django.core.exceptions import ValidationError
import re


class PasswordComplexityValidator:

    full_match = '[A-Za-z0-9\W]{8,}'
    lowercase = '[a-z]'
    uppercase = '[A-Z]'
    digits = '[0-9]'
    symbols = '[\W]'
    message = 'Your password must contain at least 1 lowercase, 1 uppercase, 1 digit and 1 symbol'

    def validate(self, password, user=None):
        if not bool(re.fullmatch(self.full_match, password)):
            raise ValidationError(self.message)
        if not bool(re.search(self.lowercase, password)):
            raise ValidationError('Your password must contain at least 1 lowercase')
        if not bool(re.search(self.uppercase, password)):
            raise ValidationError('Your password must contain at least 1 uppercase')
        if not bool(re.search(self.digits, password)):
            raise ValidationError('Your password must contain at least 1 digit')
        if not bool(re.search(self.symbols, password)):
            raise ValidationError('Your password must contain at least 1 symbol')

    def get_help_text(self):
        return self.message
