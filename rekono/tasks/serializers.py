from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from rest_framework import serializers
from tasks.models import Task
from tasks.queue import producer
from tools.enums import IntensityRank
from tools.models import Configuration, Intensity
from tools.serializers import IntensityField


class TaskSerializer(serializers.ModelSerializer):
    intensity_rank = IntensityField(source='intensity', required=False)

    class Meta:
        model = Task
        fields = (
            'id', 'target', 'process', 'tool', 'configuration',
            'intensity_rank', 'executor', 'status', 'scheduled_at',
            'scheduled_in', 'scheduled_time_unit', 'repeat_in',
            'repeat_time_unit', 'start', 'end', 'wordlists', 'executions'
        )
        read_only_fields = ('executor', 'status', 'start', 'end', 'executions')

    def validate(self, attrs):
        if not attrs.get('process') and not attrs.get('tool'):
            raise serializers.ValidationError(
                {
                    'tool': 'Invalid task. Process or tool is required',
                    'process': 'Invalid task. Process or tool is required'
                }
            )
        if attrs.get('scheduled_at') and attrs.get('scheduled_at') <= timezone.now():
            raise serializers.ValidationError({'scheduled_at': 'Scheduled datetime must be future'})
        for field, unit in [
            ('scheduled_in', 'scheduled_time_unit'),
            ('repeat_in', 'repeat_time_unit')
        ]:
            if not attrs.get(field):
                attrs[unit] = None
            elif attrs.get(field) and not attrs.get(unit):
                attrs[field] = None
        if not attrs.get('intensity'):
            attrs['intensity'] = IntensityRank.NORMAL.value
        if attrs.get('tool'):
            attrs['process'] = None
            if not attrs.get('configuration'):
                attrs['configuration'] = Configuration.objects.filter(
                    tool=attrs.get('tool'),
                    default=True
                ).first()
            intensity = Intensity.objects.filter(
                tool=attrs.get('tool'),
                value=attrs.get('intensity')
            )
            if not intensity:
                raise serializers.ValidationError(
                    {'intensity': f'Invalid intensity {attrs.get("intensity")} for tool {attrs.get("tool").name}'}      # noqa: E501
                )
        return super().validate(attrs)

    # @transaction.atomic()
    def create(self, validated_data):
        # creation_fields = [
        #     'target', 'process', 'tool', 'configuration', 'intensity', 'executor',
        #     'scheduled_at', 'scheduled_in', 'scheduled_time_unit', 'repeat_in',
        #     'repeat_time_unit'
        # ]
        # creation_data = {}
        # for field in creation_fields:
        #     creation_data[field] = validated_data.get(field)
        # task = Task.objects.create(**creation_data)
        # wordlist_types = set()
        # if validated_data.get('wordlists'):
        #     for wordlist in validated_data.get('wordlists'):
        #         if wordlist.type not in wordlist_types:
        #             task.wordlists.add(wordlist)
        #             wordlist_types.add(wordlist.type)
        #     task.save()
        task = super().create(validated_data)
        domain = None
        if self.context.get('request'):
            domain = get_current_site(self.context.get('request')).domain
        producer(task, domain)
        return task
