import os
import uuid

from resources.models import Wordlist
from rest_framework import serializers
from security import file_upload

from rekono.settings import WORDLIST_DIR


class WordlistSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True, allow_empty_file=False, write_only=True)

    class Meta:
        model = Wordlist
        fields = ('id', 'name', 'type', 'path', 'file', 'checksum', 'creator')
        read_only_fields = ('creator',)
        extra_kwargs = {
            'path': {'write_only': True, 'required': False},
            'checksum': {'write_only': True, 'required': False},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        file_upload.validate(attrs['file'], ['txt', 'text', ''], ['text/plain'])
        attrs['path'] = os.path.join(WORDLIST_DIR, f'{str(uuid.uuid4())}.txt')
        return attrs

    def save(self, **kwargs):
        kwargs['checksum'] = file_upload.store_file(kwargs.pop('file'), kwargs['path'])
        self.validated_data.pop('file')
        return super().save(**kwargs)
