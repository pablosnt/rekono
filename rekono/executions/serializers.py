from executions.models import Execution
from rest_framework import serializers


class ExecutionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Execution
        fields = ('id', 'task', 'step', 'output_plain', 'output_error', 'status', 'start', 'end')
        ordering = ['-id']
