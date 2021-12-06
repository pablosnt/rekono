from processes.models import Process, Step
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from tools.models import Configuration, Tool
from tools.serializers import ConfigurationSerializer, SimplyToolSerializer


class StepPrioritySerializer(serializers.ModelSerializer):

    class Meta:
        model = Step
        fields = ('id', 'process', 'tool', 'configuration', 'priority')
        read_only_fields = ('id', 'process', 'tool', 'configuration')


class StepSerializer(serializers.ModelSerializer):
    tool = SimplyToolSerializer(read_only=True, many=False)
    tool_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        required=True,
        source='tool',
        queryset=Tool.objects.all()
    )
    configuration = ConfigurationSerializer(read_only=True, many=False)
    configuration_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        required=False,
        source='configuration',
        queryset=Configuration.objects.all()
    )

    class Meta:
        model = Step
        fields = (
            'id', 'process', 'tool', 'tool_id', 'configuration', 'configuration_id', 'priority'
        )

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
            attrs['configuration'] = Configuration.objects.filter(
                tool=attrs.get('tool'),
                default=True
            ).first()
        steps = Step.objects.filter(
            process=attrs.get('process'),
            tool=attrs.get('tool'),
            configuration=attrs.get('configuration')
        ).count()
        if steps > 0:
            process = attrs.get('process').name
            raise serializers.ValidationError(
                {'process': f'Invalid request. Process {process} still has this step'}
            )
        return attrs


class ProcessSerializer(serializers.ModelSerializer):
    steps = SerializerMethodField(
        method_name='get_steps',
        read_only=True,
        required=False
    )
    creator = SerializerMethodField(method_name='get_creator', read_only=True, required=False)

    class Meta:
        model = Process
        fields = ('id', 'name', 'description', 'creator', 'steps')

    def get_creator(self, instance: Process) -> str:
        return instance.creator.username

    def get_steps(self, instance) -> list:
        return StepSerializer(
            instance.steps.all().order_by('tool__stage', '-priority'),
            many=True
        ).data
