from django.db import models
from security.input_validation import (validate_defect_dojo_api_key,
                                       validate_name, validate_telegram_token,
                                       validate_upload_file_size, validate_url)

# Create your models here.

class System(models.Model):
    upload_files_max_mb = models.IntegerField(default=512, validators=[validate_upload_file_size])
    telegram_bot_token = models.TextField(blank=True, null=True, validators=[validate_telegram_token])
    defect_dojo_url = models.TextField(blank=True, null=True, validators=[validate_url])
    defect_dojo_api_key = models.TextField(blank=True, null=True, validators=[validate_defect_dojo_api_key])
    defect_dojo_verify_tls = models.BooleanField(default=True)
    defect_dojo_tag = models.TextField(default='rekono', validators=[validate_name])
    defect_dojo_product_type = models.TextField(default='Rekono Project', validators=[validate_name])
    defect_dojo_test_type = models.TextField(default='Rekono Findings Import', validators=[validate_name])
    defect_dojo_test = models.TextField(default='Rekono Test', validators=[validate_name])

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return 'System'
