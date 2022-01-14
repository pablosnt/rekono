from defectdojo.views import DefectDojoFindings, DefectDojoScans
from executions.filters import ExecutionFilter
from executions.models import Execution
from executions.serializers import ExecutionSerializer
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

# Create your views here.


class ExecutionViewSet(ListModelMixin, RetrieveModelMixin, DefectDojoScans, DefectDojoFindings):
    queryset = Execution.objects.all()
    serializer_class = ExecutionSerializer
    filterset_class = ExecutionFilter
    search_fields = [
        'task__target__target', 'task__process__steps__tool__name',
        'task__process__steps__configuration__name', 'task__tool__name',
        'task__configuration__name'
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(task__target__project__members=self.request.user)

    def get_executions(self):
        return [self.get_object()]

    def get_findings(self):
        execution = self.get_object()
        findings = []
        for find_model in [
            OSINT, Host, Enumeration, Technology,
            Endpoint, Vulnerability, Credential, Exploit
        ]:
            findings.extend(find_model.objects.filter(
                execution=execution,
                is_active=True
            ).all())
        return findings
