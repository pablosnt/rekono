import os
import uuid
from typing import Any, Dict

from likes.serializers import LikeBaseSerializer
from resources.models import Wordlist
from rest_framework import serializers
from security import file_upload
from users.serializers import SimplyUserSerializer

from rekono.settings import WORDLIST_DIR


class WordlistSerializer(serializers.ModelSerializer, LikeBaseSerializer):
    '''Serializer to manage wordlists via API.'''

    # Wordlist file, to allow the wordlist files upload to the server
    file = serializers.FileField(required=True, allow_empty_file=False, write_only=True)
    creator = SimplyUserSerializer(many=False, read_only=True)                  # Creator details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Wordlist
        # Wordlist fields exposed via API
        fields = ('id', 'name', 'type', 'path', 'file', 'checksum', 'size', 'creator', 'liked', 'likes')
        read_only_fields = ('creator',)                                         # Read only field
        # Parameters used in write operations, but they will be generated automatically from uploaded file
        extra_kwargs = {
            'path': {'write_only': True, 'required': False},
            'checksum': {'write_only': True, 'required': False},
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        attrs = super().validate(attrs)                                         # Original data validation
        file_upload.validate(attrs['file'], ['txt', 'text', ''], ['text/plain'])    # Validate the uploaded file type
        return attrs

    def save(self, **kwargs: Any) -> Wordlist:
        '''Save changes in instance.

        Returns:
            Wordlist: Instance after apply changes
        '''
        self.validated_data['path'] = os.path.join(WORDLIST_DIR, f'{str(uuid.uuid4())}.txt')    # Generate filename
        self.validated_data['checksum'] = file_upload.store_file(               # Store uploaded file in server
            self.validated_data.pop('file'),
            self.validated_data['path']
        )
        with open(self.validated_data['path'], 'rb+') as wordlist_file:         # Open uploaded file
            self.validated_data['size'] = len(wordlist_file.readlines())        # Count entries from uploaded file
        return super().save(**kwargs)

    def update(self, instance: Wordlist, validated_data: Dict[str, Any]) -> Wordlist:
        '''Update instance from validated data.

        Args:
            instance (Wordlist): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Returns:
            Wordlist: Updated instance
        '''
        old_path = instance.path                                                # Get original wordlist filepath
        updated_instance = super().update(instance, validated_data)             # Update wordlist
        # Remove original wordlist filepath, since a new wordlist file has been uploaded
        os.remove(old_path)
        return updated_instance
