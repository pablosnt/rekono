from django.db import models
from rest_framework.exceptions import ParseError
from processes.models import Process, Step
from rest_framework import serializers
from tools.models import Configuration


class StepPrioritySerializer(serializers.ModelSerializer):
    priority = serializers.CharField(source='get_priority_display')

    class Meta:
        model = Step
        fields = ('id', 'process', 'tool', 'configuration', 'priority')
        read_only_fields = ('id', 'process', 'tool', 'configuration')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        priority = attrs.pop('get_priority_display')
        try:
            attrs['priority'] = Step.Priority(int(priority)).value
        except ValueError:
            raise ParseError(f'Invalid value {priority} for priority field')
        return attrs


class StepSerializer(serializers.ModelSerializer):
    priority = serializers.CharField(source='get_priority_display')

    class Meta:
        model = Step
        fields = ('id', 'process', 'tool', 'configuration', 'priority')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        configuration = attrs.get('configuration')
        if configuration:
            check_configuration = Configuration.objects.filter(
                tool=attrs.get('tool'),
                id=configuration.id
            ).count()
            if check_configuration == 0:
                configuration = None
        if not configuration:
            configuration = Configuration.objects.filter(
                tool=attrs.get('tool'),
                default=True
            ).first()
        attrs['configuration'] = configuration
        priority = attrs.pop('get_priority_display')
        try:
            attrs['priority'] = Step.Priority(int(priority)).value
        except ValueError:
            raise ParseError(f'Invalid value {priority} for priority field')
        steps = Step.objects.filter(
            process=attrs.get('process'),
            tool=attrs.get('tool'),
            configuration=configuration
        ).count()
        if steps > 0:
            process = attrs.get('process').name
            raise ParseError(
                f'Invalid request. Process {process} still has this step'
            )
        return attrs


class ProcessSerializer(serializers.ModelSerializer):
    steps = StepSerializer(read_only=True, many=True, required=False)

    class Meta:
        model = Process
        fields = ('id', 'name', 'description', 'creator', 'steps')
        read_only_fields = ('creator', 'steps')
