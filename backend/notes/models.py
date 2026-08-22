"""Model of the notes that the auditors write."""

from django.db import models
from taggit.managers import TaggableManager

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
from framework.models import BaseLike
from projects.models import Project
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from targets.models import Target
from tasks.models import Task


class Note(BaseLike):
    """Note about a project or about one of the things discovered in it.

    A note always belongs to a project and only one of the other links can be set,
    so a note is always about one thing, and it's removed together with it.

    Attributes:
        project: Project that the note belongs to.
        target: Target that the note is about.
        task: Task that the note is about.
        osint: OSINT finding that the note is about.
        host: Host that the note is about.
        port: Port that the note is about.
        path: Path that the note is about.
        credential: Credential that the note is about.
        technology: Technology that the note is about.
        vulnerability: Vulnerability that the note is about.
        exploit: Exploit that the note is about.
        title: Title of the note.
        body: Content of the note, as rich text.
        tags: Tags that classify the note.
        owner: User that wrote the note.
        public: Whether the other project members can read the note.
        forked_from: Public note that this one is a copy of.
        created_at: Date when the note was written.
        updated_at: Date when the note was updated for the last time.
    """

    project = models.ForeignKey(Project, related_name="notes", on_delete=models.CASCADE)
    target = models.ForeignKey(Target, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    osint = models.ForeignKey(OSINT, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    host = models.ForeignKey(Host, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    port = models.ForeignKey(Port, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    path = models.ForeignKey(Path, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    credential = models.ForeignKey(Credential, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    technology = models.ForeignKey(Technology, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    vulnerability = models.ForeignKey(
        Vulnerability, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    exploit = models.ForeignKey(Exploit, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(max_length=200, validators=[Validator(Regex.NAME, code="title")])
    body = models.TextField(blank=True, null=True)
    tags = TaggableManager()
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    public = models.BooleanField(default=False)
    forked_from = models.ForeignKey("Note", related_name="forks", on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    _project_field = "project"

    def __str__(self) -> str:
        """Return the title of the note, with the thing that it's about."""
        item = next(
            iter(
                [
                    link
                    for link in [
                        self.target,
                        self.task,
                        self.osint,
                        self.host,
                        self.port,
                        self.path,
                        self.credential,
                        self.technology,
                        self.vulnerability,
                        self.exploit,
                    ]
                    if link
                ]
            ),
            None,
        )
        if not item:
            item = self.project
        return " - ".join([item.__str__(), self.title])
