import os
import uuid

from resources.models import Wordlist
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from security import file_upload
from users.serializers import SimplyUserSerializer

from rekono.settings import WORDLIST_DIR


class WordlistSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True, allow_empty_file=False, write_only=True)
    creator = SerializerMethodField(method_name='get_creator', read_only=True, required=False)

    class Meta:
        model = Wordlist
        fields = ('id', 'name', 'type', 'path', 'file', 'checksum', 'size', 'creator')
        read_only_fields = ('creator',)
        extra_kwargs = {
            'path': {'write_only': True, 'required': False},
            'checksum': {'write_only': True, 'required': False},
        }

    def get_creator(self, instance: Wordlist) -> SimplyUserSerializer:
        return SimplyUserSerializer(instance.creator).data

    def validate(self, attrs):
        attrs = super().validate(attrs)
        file_upload.validate(attrs['file'], ['txt', 'text', ''], ['text/plain'])
        return attrs

    def save(self, **kwargs):
        self.validated_data['path'] = os.path.join(WORDLIST_DIR, f'{str(uuid.uuid4())}.txt')
        self.validated_data['checksum'] = file_upload.store_file(
            self.validated_data.pop('file'),
            self.validated_data['path']
        )
        with open(self.validated_data['path'], 'rb+') as wordlist_file:
            self.validated_data['size'] = len(wordlist_file.readlines())
        return super().save(**kwargs)

    def update(self, instance, validated_data):
        old_path = instance.path
        updated_instance = super().update(instance, validated_data)
        os.remove(old_path)
        return updated_instance
