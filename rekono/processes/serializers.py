from processes.models import Process, Step
from rest_framework import serializers


class StepSerializer(serializers.ModelSerializer):
    priority = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Step
        fields = ('id', 'tool', 'configuration', 'priority')


class ProcessSerializer(serializers.ModelSerializer):
    steps = StepSerializer(read_only=True, many=True, required=False)

    class Meta:
        model = Process
        fields = ('id', 'name', 'description', 'creator', 'steps')
        read_only_fields = ('creator', 'steps')
