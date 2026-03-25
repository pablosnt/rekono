"""Django REST framework serializers for notes management.

Serializer classes for converting note models to/from JSON for API operations.
Includes validation logic for entity relationships, forking behavior, and
collaborative features with tag support.

Write operations accept entity IDs via *_id fields (e.g. target_id, task_id),
while read operations return full entity objects through the serializers defined
in each entity's backend module. The project field always uses an integer ID for
both read and write.
"""

from typing import Any, cast

from rest_framework.fields import ValidationError
from rest_framework.serializers import PrimaryKeyRelatedField, SerializerMethodField
from taggit.serializers import TaggitSerializer

from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Host,
    Path,
    Port,
    Technology,
    Vulnerability,
)
from findings.serializers import (
    CredentialSerializer,
    ExploitSerializer,
    HostSerializer,
    OSINTSerializer,
    PathSerializer,
    PortWithHostSerializer,
    TechnologySerializer,
    VulnerabilitySerializer,
)
from framework.fields import TagField
from framework.models import BaseModel
from framework.serializers import LikeSerializer
from notes.models import Note
from targets.models import Target
from targets.serializers import SimpleTargetSerializer
from tasks.models import Task
from tasks.serializers import TaskSerializer
from users.serializers import SimpleUserSerializer

# List of all possible entity relationships for notes (including project).
# Used for validation and project context determination.
links = [
    "project",
    "target",
    "task",
    "osint",
    "host",
    "port",
    "path",
    "credential",
    "technology",
    "vulnerability",
    "exploit",
]


class NoteSerializer(TaggitSerializer, LikeSerializer):
    """Serializer for Note model with collaborative features.

    Handles serialization and deserialization of Note objects for API operations.
    Includes validation logic for entity relationships, forking behavior, and
    tag management with computed fields for fork status.

    Write operations accept entity IDs via *_id fields (e.g. target_id, task_id),
    while read operations return full entity objects through the serializers defined
    in each entity's backend module. The project field uses an integer ID for both
    read and write.

    Attributes:
        owner (SimpleUserSerializer): Serialized user information for note owner
        tags (TagField): Tag field for note categorization
        forked (SerializerMethodField): Current user's fork of this note, if any
        target_id (PrimaryKeyRelatedField): Target ID for write operations (write-only)
        target (SimpleTargetSerializer): Target entity for read operations (read-only)
        task_id (PrimaryKeyRelatedField): Task ID for write operations (write-only)
        task (TaskSerializer): Task entity for read operations (read-only)
        osint_id (PrimaryKeyRelatedField): OSINT ID for write operations (write-only)
        osint (OSINTSerializer): OSINT entity for read operations (read-only)
        host_id (PrimaryKeyRelatedField): Host ID for write operations (write-only)
        host (HostSerializer): Host entity for read operations (read-only)
        port_id (PrimaryKeyRelatedField): Port ID for write operations (write-only)
        port (PortWithHostSerializer): Port entity for read operations (read-only)
        path_id (PrimaryKeyRelatedField): Path ID for write operations (write-only)
        path (PathSerializer): Path entity for read operations (read-only)
        credential_id (PrimaryKeyRelatedField): Credential ID for write operations (write-only)
        credential (CredentialSerializer): Credential entity for read operations (read-only)
        technology_id (PrimaryKeyRelatedField): Technology ID for write operations (write-only)
        technology (TechnologySerializer): Technology entity for read operations (read-only)
        vulnerability_id (PrimaryKeyRelatedField): Vulnerability ID for write operations (write-only)
        vulnerability (VulnerabilitySerializer): Vulnerability entity for read operations (read-only)
        exploit_id (PrimaryKeyRelatedField): Exploit ID for write operations (write-only)
        exploit (ExploitSerializer): Exploit entity for read operations (read-only)
    """

    owner = SimpleUserSerializer(many=False, read_only=True)
    tags = TagField()
    forked = SerializerMethodField(read_only=True)
    target_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, allow_null=True, source="target", queryset=Target.objects.all()
    )
    target = SimpleTargetSerializer(many=False, read_only=True)
    task_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, allow_null=True, source="task", queryset=Task.objects.all()
    )
    task = TaskSerializer(many=False, read_only=True)
    osint_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, allow_null=True, source="osint", queryset=OSINT.objects.all()
    )
    osint = OSINTSerializer(many=False, read_only=True)
    host_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, allow_null=True, source="host", queryset=Host.objects.all()
    )
    host = HostSerializer(many=False, read_only=True)
    port_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, allow_null=True, source="port", queryset=Port.objects.all()
    )
    port = PortWithHostSerializer(many=False, read_only=True)
    path_id = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, allow_null=True, source="path", queryset=Path.objects.all()
    )
    path = PathSerializer(many=False, read_only=True)
    credential_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=False,
        allow_null=True,
        source="credential",
        queryset=Credential.objects.all(),
    )
    credential = CredentialSerializer(many=False, read_only=True)
    technology_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=False,
        allow_null=True,
        source="technology",
        queryset=Technology.objects.all(),
    )
    technology = TechnologySerializer(many=False, read_only=True)
    vulnerability_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=False,
        allow_null=True,
        source="vulnerability",
        queryset=Vulnerability.objects.all(),
    )
    vulnerability = VulnerabilitySerializer(many=False, read_only=True)
    exploit_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=False,
        allow_null=True,
        source="exploit",
        queryset=Exploit.objects.all(),
    )
    exploit = ExploitSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for the NoteSerializer.

        Attributes:
            model (Model): The Note model to serialize
            fields (tuple): Field names to include in serialization.
                Entity relationships use *_id for write and plain name for read.
            read_only_fields (tuple): Fields that cannot be modified via API
        """

        model = Note
        fields = (
            "id",
            "project",
            "target_id",
            "target",
            "task_id",
            "task",
            "osint_id",
            "osint",
            "host_id",
            "host",
            "port_id",
            "port",
            "path_id",
            "path",
            "credential_id",
            "credential",
            "technology_id",
            "technology",
            "vulnerability_id",
            "vulnerability",
            "exploit_id",
            "exploit",
            "title",
            "body",
            "tags",
            "owner",
            "public",
            "forked",
            "forked_from",
            "forks",
            "created_at",
            "updated_at",
            "liked",
            "likes",
        )
        read_only_fields = (
            "owner",
            "forked",
            "forked_from",
            "forks",
            "created_at",
            "updated_at",
            "liked",
            "likes",
        )

    def get_forked(self, instance: Any) -> int | None:
        """Check if the current user has forked this note.

        Args:
            instance (Note): The note instance being serialized

        Returns:
            int | None: ID note of the current user's fork, if any
        """
        forks = instance.forks.filter(owner=self.context.get("request").user)
        return forks.first().id if forks.exists() else None

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate note data and ensure single entity association.

        Ensures that a note is associated with exactly one entity and automatically
        sets the project context based on the associated entity. Validation uses
        source names (e.g. "target", not "target_id") since PrimaryKeyRelatedField
        maps *_id inputs to their source names in attrs.

        Args:
            attrs (dict[str, Any]): Validated field data

        Returns:
            dict[str, Any]: Validated and processed field data

        Raises:
            ValidationError: If no project context can be determined
        """
        attrs = super().validate(attrs)
        # Find the first (most specific) entity relationship in the data.
        # Reversed order ensures we get the most specific entity first
        # (exploit > vulnerability > technology > ... > target > project).
        # Attrs use source names (e.g. "target") because PrimaryKeyRelatedField
        # with source="target" stores the resolved instance under "target" in attrs.
        data_links = [link for link in reversed(links) if attrs.get(link) is not None]
        if len(data_links) > 0:
            # Clear all other entity relationships to ensure only one is active
            for link in links:
                if link != data_links[0]:
                    attrs[link] = None
            # Set project context from the active entity
            attrs["project"] = cast(BaseModel, attrs.get(data_links[0])).parent_project
        return attrs

    def update(self, instance: Note, validated_data: dict[str, Any]) -> Note:
        """Update note instance with validation for project changes and fork behavior.

        Enforces project immutability and handles fork unlinking when notes become private.
        Ensures forked notes maintain proper visibility behavior.

        Args:
            instance (Note): The note instance being updated
            validated_data (dict[str, Any]): The validated update data

        Returns:
            Note: The updated note instance

        Raises:
            ValidationError: If attempting to change the project of an existing note
        """
        if instance.project != validated_data.get("project"):
            raise ValidationError("You are not allowed to change the project of a note", code="project")
        # Forked notes cannot be made public - they must remain private
        if instance.forked_from and validated_data.get("public", True):
            validated_data["public"] = False
        # Track if we need to unlink forks when a note becomes private
        unlink_forks = instance.public and not validated_data.get("public", False)
        # Perform the update
        new_instance = super().update(instance, validated_data)
        # If the note became private, unlink all its forks
        if unlink_forks:
            Note.objects.filter(public=False, forked_from=new_instance).update(forked_from=None)
        return new_instance
