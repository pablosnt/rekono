import re

from django.core.exceptions import ValidationError
from users.models import User


class PasswordComplexityValidator:
    '''Rekono password complexity validator.'''

    full_match = r'[A-Za-z0-9\W]{12,}'                                          # Full match with all requirements
    lowercase = r'[a-z]'                                                        # At least one lowercase
    uppercase = r'[A-Z]'                                                        # At least one uppercase
    digits = r'[0-9]'                                                           # At least one digit
    symbols = r'[\W]'                                                           # At least one symbol
    message = 'Your password must contain at least 1 lowercase, 1 uppercase, 1 digit and 1 symbol'

    def validate(self, password: str, user: User = None) -> None:
        '''Validate if password match the complexity requirements.

        Args:
            password (str): Password to check
            user (User, optional): User that is establishing the password. Defaults to None.

        Raises:
            ValidationError: Raised if password doesn't match the complexity requirements
        '''
        if not bool(re.fullmatch(self.full_match, password)):                   # Full check
            raise ValidationError(self.message)
        if not bool(re.search(self.lowercase, password)):                       # Lower case check
            raise ValidationError('Your password must contain at least 1 lowercase')
        if not bool(re.search(self.uppercase, password)):                       # Upper case check
            raise ValidationError('Your password must contain at least 1 uppercase')
        if not bool(re.search(self.digits, password)):                          # Digits check
            raise ValidationError('Your password must contain at least 1 digit')
        if not bool(re.search(self.symbols, password)):                         # Symbols check
            raise ValidationError('Your password must contain at least 1 symbol')

    def get_help_text(self) -> str:
        '''Get help message.

        Returns:
            str: Help message
        '''
        return self.message
