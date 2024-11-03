from typing import Any

from django.db.models import Count
from django_rq.utils import get_statistics
from drf_spectacular.utils import extend_schema, inline_serializer
from findings.enums import TriageStatus
from findings.models import OSINT, Credential, Exploit, Vulnerability
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from security.authorization.permissions import IsAdmin
from stats.serializers import (
    ActivityStatsSerializer,
    HostsStatsSerializer,
    RQStatsSerializer,
    ScopeSerializer,
    StatsSerializer,
    TriagingStatsSerializer,
    VulnerabilityStatsSerializer,
)


class RQStatsView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(request=None, responses=RQStatsSerializer)
    def get(self, request: Request) -> Response:
        return Response(
            RQStatsSerializer(
                {queue["name"]: queue for queue in get_statistics().get("queues", [])}
            ).data,
            status=HTTP_200_OK,
        )


class StatsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StatsSerializer

    def get_serializer_class(self) -> type[StatsSerializer]:
        return self.serializer_class

    @extend_schema(parameters=[ScopeSerializer])
    def get(self, request: Request) -> Response:
        serializer = self.serializer_class(
            data=request.query_params, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActivityStatsView(StatsView):
    serializer_class = ActivityStatsSerializer


class HostsStatsView(StatsView):
    serializer_class = HostsStatsSerializer


class VulnerabilityStatsView(StatsView):
    serializer_class = VulnerabilityStatsSerializer


class TriagingStatsView(StatsView):
    serializer_class = TriagingStatsSerializer


# TODO: Evolution
#   Per day: findings, fixed findings, hosts, services
