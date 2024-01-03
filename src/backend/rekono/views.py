from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK
from security.authorization.permissions import IsAdmin
from rest_framework.request import Request
from rest_framework.response import Response
from django_rq.utils import get_statistics
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

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
                    "executions-queue": inline_serializer(
                        name="QueueStats",
                        fields={k: serializers.IntegerField() for k in exposed_fields},
                    ),
                    "findings-queue": inline_serializer(
                        name="QueueStats",
                        fields={k: serializers.IntegerField() for k in exposed_fields},
                    ),
                    "tasks-queue": inline_serializer(
                        name="QueueStats",
                        fields={k: serializers.IntegerField() for k in exposed_fields},
                    ),
                },
            )
        },
    )
    def get(self, request: Request) -> Response:
        stats = {}
        for queue in get_statistics().get("queues", []):
            stats[queue["name"]] = {
                k: v for k, v in queue.items() if k in exposed_fields
            }
        return Response(stats, status=HTTP_200_OK)
