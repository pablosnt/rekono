from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.utils import timezone
from findings.enums import PortStatus
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from rest_framework import serializers
from tasks.models import Task
from tasks.queue import producer
from tools.enums import IntensityRank
from tools.models import Configuration, Intensity
from tools.serializers import IntensityField


class ManualFindingModelSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['is_manual'] = True
        return super().create(validated_data)

    def get_findings(self, finding):
        return [finding]


# Disabled because currently there are no Inputs related to these types
# class ManualVulnerabilitySerializer(ManualFindingModelSerializer):

#     class Meta:
#         model = Vulnerability
#         fields = ('id', 'enumeration', 'technology', 'name', 'severity', 'cve', 'task')
#         extra_kwargs = {
#             'enumeration': {'write_only': True, 'required': False},
#             'technology': {'write_only': True, 'required': False},
#             'task': {'write_only': True}
#         }


# Disabled because currently there are no Inputs related to these types
# class ManualTechnologySerializer(ManualFindingModelSerializer):
#     vulnerability = ManualVulnerabilitySerializer(read_only=False, many=True, required=False)

#     class Meta:
#         model = Technology
#         fields = ('id', 'enumeration', 'name', 'version', 'task', 'vulnerability')
#         extra_kwargs = {
#             'enumeration': {'write_only': True},
#             'task': {'write_only': True}
#         }

#     def create(self, validated_data):
#         vulnerability_data = validated_data.pop('vulnerability')
#         technology = super().create(validated_data)
#         for vulnerability in vulnerability_data:
#             vulnerability['technology'] = technology
#             ManualVulnerabilitySerializer().create(vulnerability)
#         return technology

#     def get_findings(self, finding):
#         return [finding] + list(finding.vulnerability.all())


class ManualEndpointSerializer(ManualFindingModelSerializer):
    class Meta:
        model = Endpoint
        fields = ('id', 'enumeration', 'endpoint', 'task')
        extra_kwargs = {
            'enumeration': {'write_only': True},
            'task': {'write_only': True}
        }


class ManualEnumerationSerializer(ManualFindingModelSerializer):
    endpoint = ManualEndpointSerializer(read_only=False, many=True, required=False)
    # Disabled because currently there are no Inputs related to these types
    # technology = ManualTechnologySerializer(read_only=False, many=True, required=False)
    # vulnerability = ManualVulnerabilitySerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Enumeration
        fields = (
            'id', 'host', 'port', 'protocol', 'service', 'task', 'endpoint'
            # 'technology', 'vulnerability'
        )
        extra_kwargs = {
            'host': {'write_only': True},
            'port_status': {'required': False},
            'task': {'write_only': True},
        }

    def create(self, validated_data):
        endpoint_data = validated_data.pop('endpoint')
        # technology_data = validated_data.pop('technology')
        # vulnerability_data = validated_data.pop('vulnerability')
        enumeration = super().create(validated_data)
        for serializer, items in [
            (ManualEndpointSerializer, endpoint_data or []),
            # (ManualTechnologySerializer, technology_data or []),
            # (ManualVulnerabilitySerializer, vulnerability_data or [])
        ]:
            for item in items:
                item['enumeration'] = enumeration
                serializer().create(item)
        return enumeration

    def get_findings(self, finding):
        return [finding] + list(finding.endpoint.all())


class ManualHostSerializer(ManualFindingModelSerializer):
    enumeration = ManualEnumerationSerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Host
        fields = ('id', 'address', 'os_type', 'task', 'enumeration')
        extra_kwargs = {'task': {'write_only': True}}

    def create(self, validated_data):
        enumeration_data = validated_data.pop('enumeration')
        host = super().create(validated_data)
        for enumeration in enumeration_data:
            enumeration['host'] = host
            ManualEnumerationSerializer().create(enumeration)
        return host

    def get_findings(self, finding):
        return [finding] + list(finding.enumeration.all())


# Disabled because currently there are no Inputs related to these types
# class ManualCredentialSerializer(ManualFindingModelSerializer):
#     class Meta:
#         model = Credential
#         fields = ('id', 'email', 'username', 'secret', 'task')
#         extra_kwargs = {'task': {'write_only': True}}


# Disabled because currently there are no Inputs related to these types
# class ManualOSINTSerializer(ManualFindingModelSerializer):
#     class Meta:
#         model = OSINT
#         fields = ('id', 'data', 'data_type', 'task')
#         extra_kwargs = {'task': {'write_only': True}}


class TaskSerializer(serializers.ModelSerializer):
    intensity_rank = IntensityField(source='intensity')
    host = ManualHostSerializer(read_only=False, many=True, required=False)
    # Disabled because currently there are no Inputs related to these types
    # osint = ManualOSINTSerializer(read_only=False, many=True, required=False)
    # credential = ManualCredentialSerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Task
        fields = (
            'id', 'target', 'process', 'tool', 'configuration',
            'intensity_rank', 'executor', 'status', 'scheduled_at',
            'scheduled_in', 'scheduled_time_unit', 'repeat_in',
            'repeat_time_unit', 'start', 'end', 'wordlists',
            # 'osint', 'credential'
            'host', 'executions'
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

    @transaction.atomic()
    def create(self, validated_data):
        creation_fields = [
            'target', 'process', 'tool', 'configuration', 'intensity', 'executor',
            'scheduled_at', 'scheduled_in', 'scheduled_time_unit', 'repeat_in',
            'repeat_time_unit'
        ]
        creation_data = {}
        for field in creation_fields:
            creation_data[field] = validated_data.get(field)
        task = Task.objects.create(**creation_data)
        wordlist_types = set()
        if validated_data.get('wordlists'):
            for wordlist in validated_data.get('wordlists'):
                if wordlist.type not in wordlist_types:
                    task.wordlists.add(wordlist)
                    wordlist_types.add(wordlist.type)
            task.save()
        manual_findings = []
        finding_fields = [
            # ('osint', ManualOSINTSerializer),
            ('host', ManualHostSerializer),
            # ('credential', ManualCredentialSerializer)
        ]
        for field, serializer in finding_fields:
            if validated_data.get(field):
                for item in validated_data.get(field):
                    item['task'] = task
                    finding = serializer().create(item)
                    manual_findings.extend(serializer().get_findings(finding))
        # Resources are included as manual findings to make executions easier
        manual_findings.extend(list(task.wordlists.all()))
        domain = None
        if self.context.get('request'):
            domain = get_current_site(self.context.get('request')).domain
        producer(task, manual_findings, domain)
        return task
