from typing import List, Type

from defectdojo.views import DefectDojoFindings, DefectDojoScans
from django.db.models import QuerySet
from executions.filters import ExecutionFilter
from executions.models import Execution
from executions.serializers import ExecutionSerializer
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Finding, Host, Technology, Vulnerability)
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

# Create your views here.


class ExecutionViewSet(ListModelMixin, RetrieveModelMixin, DefectDojoScans, DefectDojoFindings):
    '''Execution ViewSet that includes: get, retrieve and import Defect-Dojo features.'''

    queryset = Execution.objects.all().order_by('-id')
    serializer_class = ExecutionSerializer
    filterset_class = ExecutionFilter
    search_fields = [                                                           # Fields used to search executions
        'task__target__target', 'task__process__steps__tool__name',
        'task__process__steps__configuration__name', 'task__tool__name',
        'task__configuration__name'
    ]

    def get_queryset(self) -> QuerySet:
        '''Get the Execution queryset that the user is allowed to get, based on project members.

        Returns:
            QuerySet: Execution queryset
        '''
        queryset = super().get_queryset()
        return queryset.filter(task__target__project__members=self.request.user)

    def get_executions(self) -> List[Execution]:
        '''Get executions list associated to the current instance. Needed for Defect-Dojo integration.

        Returns:
            List[Execution]: Executions list associated to the current instance
        '''
        return [self.get_object()]

    def get_findings(self) -> List[Finding]:
        '''Get findings list associated to the current instance. Needed for Defect-Dojo integration.

        Returns:
            List[Finding]: Findings list associated to the current instance
        '''
        execution = self.get_object()
        findings: List[Finding] = []
        finding_models: List[Type[Finding]] = [
            OSINT, Host, Enumeration, Technology, Endpoint, Vulnerability, Credential, Exploit
        ]
        for finding_model in finding_models:
            # Search active findings related to this execution
            findings.extend(list(finding_model.objects.filter(execution=execution, is_active=True).all()))
        return findings
