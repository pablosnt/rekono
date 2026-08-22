"""Serializers of the note endpoints."""

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
    PortSerializer,
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

# Everything that a note can be about, ordered from the most general one to the most specific
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
    """Serializer of a note and of the thing that it's about.

    The thing that the note is about is written by its identifier, through the
    fields whose name ends in "_id", and read as the whole object, so the notes can
    be shown next to it without having to request it separately. The project is the
    only exception, since it's always read and written as an identifier.

    The links are declared from the most general scope to the most specific one, and
    only the most specific one survives the validation, so a note sent with both a
    host and one of its ports ends up being about the port alone.

    Attributes:
        owner: User that wrote the note.
        tags: Tags that classify the note.
        forked: Copy of this note that belongs to the user that makes the request.
        target_id: Target that the note is about, the widest scope after the project.
        target: The linked target, read as the whole object.
        task_id: Task that the note is about.
        task: The linked task, read as the whole object.
        osint_id: OSINT finding that the note is about, the least specific of the
          finding links.
        osint: The linked OSINT finding, read as the whole object.
        host_id: Host that the note is about.
        host: The linked host, read as the whole object.
        port_id: Port that the note is about, which wins over its host.
        port: The linked port, read as the whole object.
        path_id: Path that the note is about, which wins over its port.
        path: The linked path, read as the whole object.
        credential_id: Credential that the note is about.
        credential: The linked credential, read as the whole object.
        technology_id: Technology that the note is about.
        technology: The linked technology, read as the whole object.
        vulnerability_id: Vulnerability that the note is about.
        vulnerability: The linked vulnerability, read as the whole object.
        exploit_id: Exploit that the note is about, the most specific link, which
          wins over every other one.
        exploit: The linked exploit, read as the whole object.
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
    port = PortSerializer(many=False, read_only=True)
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
        """Serializer configuration for the notes."""

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
        """Get the copy of this note that the user forked from it.

        Args:
            instance: Note being serialized.

        Returns:
            The identifier of their copy, or None if they don't have one.
        """
        forks = instance.forks.filter(owner=self.context.get("request").user)
        return forks.first().id if forks.exists() else None

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check the note data and keep only the thing that the note is about.

        Args:
            attrs: Note fields sent by the user, which may link several things.

        Returns:
            The validated data, with all the links removed except the most specific
            one, and with the project of that link, so the note always belongs to
            the same project as the thing that it's about.
        """
        attrs = super().validate(attrs)
        # The links are named after the source of their write field, since that's where
        # PrimaryKeyRelatedField leaves the object that it resolves
        data_links = [link for link in reversed(links) if attrs.get(link) is not None]
        if len(data_links) > 0:
            for link in links:
                if link != data_links[0]:
                    attrs[link] = None
            attrs["project"] = cast(BaseModel, attrs.get(data_links[0])).parent_project
        return attrs

    def update(self, instance: Note, validated_data: dict[str, Any]) -> Note:
        """Update a note, keeping the project and the visibility of its forks.

        Args:
            instance: Note being updated.
            validated_data: Note fields, plus the project that the validate method
              resolves from the object that the note is linked to. Its public field
              is forced to False for a fork, so it isn't always the value sent.

        Returns:
            The updated note. A note that is a fork can never be made public, and
            the forks of a note that stops being public are unlinked from it, so
            nobody keeps a reference to a note that they can't read anymore.

        Raises:
            ValidationError: If the note is moved to another project.
        """
        if instance.project != validated_data.get("project"):
            raise ValidationError("You are not allowed to change the project of a note", code="project")
        if instance.forked_from and validated_data.get("public", True):
            validated_data["public"] = False
        # Captured before the update so the pre-change visibility is still available afterwards
        unlink_forks = instance.public and not validated_data.get("public", False)
        new_instance = super().update(instance, validated_data)
        if unlink_forks:
            Note.objects.filter(public=False, forked_from=new_instance).update(forked_from=None)
        return new_instance
