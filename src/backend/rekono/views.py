from typing import Any

from django_rq.utils import get_statistics
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from security.authorization.permissions import IsAdmin

exposed_fields = [
    "jobs",  # Enqueued jobs
    "workers",
    "finished_jobs",
    "started_jobs",  # Running jobs
    "deferred_jobs",
    "failed_jobs",
    "scheduled_jobs",
]


class RQStatsView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name="RQStats",
                fields={
                    "tasks": inline_serializer(
                        name="TasksStats",
                        fields={k: serializers.IntegerField() for k in exposed_fields},
                    ),
                    "executions": inline_serializer(
                        name="ExecutionsStats",
                        fields={k: serializers.IntegerField() for k in exposed_fields},
                    ),
                    "findings": inline_serializer(
                        name="FindingsStats",
                        fields={k: serializers.IntegerField() for k in exposed_fields},
                    ),
                    "monitor": inline_serializer(
                        name="MonitorStats",
                        fields={k: serializers.IntegerField() for k in exposed_fields},
                    ),
                },
            )
        },
    )
    def get(self, request: Request) -> Response:
        stats: dict[str, dict[str, Any]] = {
            "tasks": {},
            "executions": {},
            "findings": {},
            "monitor": {},
        }
        for queue in get_statistics().get("queues", []):
            stats[queue["name"]] = {
                k: v for k, v in queue.items() if k in exposed_fields
            }
        return Response(stats, status=HTTP_200_OK)
