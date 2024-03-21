from findings.models import OSINT
from rest_framework.serializers import ModelSerializer


class FindingSerializer(ModelSerializer):
    class Meta:
        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = (
            "id",
            "executions",
            "triage_status",
            "triage_comment",
            "defect_dojo_id",
            "hacktricks_link",
        )


class TriageFindingSerializer(ModelSerializer):
    class Meta:
        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = ("id", "triage_status", "triage_comment")
