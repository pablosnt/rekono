from django.conf import settings
from django.db import models
from security.input_validation import (DD_KEY_REGEX, TELEGRAM_TOKEN_REGEX,
                                       validate_boolean_value, validate_name,
                                       validate_number_value,
                                       validate_text_value, validate_url)

# Create your models here.

class Setting(models.Model):
    field = models.TextField(max_length=30, unique=True)
    # This should be encrypted to protect Telegram token and Defect-Dojo API key, but there isn't a good way to do that
    value = models.TextField(max_length=100, blank=True, null=True)
    private = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.field

    def validate(self) -> None:
        validators = {
            'otp_expiration_hours': (int, validate_number_value, [1, 72]),
            'upload_files_max_mb': (int, validate_number_value, [100, 1000]),
            'telegram_bot_name': (str, validate_name, []),
            'telegram_bot_token': (str, validate_text_value, [TELEGRAM_TOKEN_REGEX]),
            'defect_dojo_url': (str, validate_url, []),
            'defect_dojo_api_key': (str, validate_text_value, [DD_KEY_REGEX]),
            'defect_dojo_verify_tls': (None, validate_boolean_value, []),
            'defect_dojo_tag': (str, validate_name, []),
            'defect_dojo_product_type': (str, validate_name, []),
            'defect_dojo_test_type': (str, validate_name, []),
            'defect_dojo_test': (str, validate_name, []),
        }
        value_type, validator, args = validators[self.field]
        value = self.value if not value_type else value_type(self.value)
        args.insert(0, value)
        validator(*args)
