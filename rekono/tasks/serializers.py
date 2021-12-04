from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.utils import timezone
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


class ManualExploitSerializer(ManualFindingModelSerializer):
    class Meta:
        model = Exploit
        fields = ('id', 'vulnerability', 'technology', 'name', 'reference', 'task')
        extra_kwargs = {
            'vulnerability': {'write_only': True},
            'technology': {'write_only': True},
            'task': {'write_only': True}
        }


class ManualVulnerabilitySerializer(ManualFindingModelSerializer):
    exploit = ManualExploitSerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Vulnerability
        fields = ('id', 'technology', 'name', 'severity', 'cve', 'task', 'exploit')
        extra_kwargs = {
            'technology': {'write_only': True},
            'task': {'write_only': True}
        }

    def create(self, validated_data):
        creation_fields = ['technology', 'name', 'severity', 'cve', 'task']
        creation_data = {'is_manual': True}
        for field in creation_fields:
            creation_data[field] = validated_data.get(field)
        vulnerability = Vulnerability.objects.create(**creation_data)
        if validated_data.get('exploit'):
            for e in validated_data.get('exploit'):
                field_data = e.copy()
                field_data['vulnerability'] = vulnerability
                ManualExploitSerializer().create(field_data)
        return vulnerability

    def get_findings(self, finding):
        return [finding] + list(finding.exploit.all())


class ManualTechnologySerializer(ManualFindingModelSerializer):
    vulnerability = ManualVulnerabilitySerializer(read_only=False, many=True, required=False)
    exploit = ManualExploitSerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Technology
        fields = ('id', 'enumeration', 'name', 'version', 'task', 'vulnerability', 'exploit')
        extra_kwargs = {
            'enumeration': {'write_only': True},
            'task': {'write_only': True}
        }

    def create(self, validated_data):
        creation_fields = ['enumeration', 'name', 'version', 'task']
        creation_data = {'is_manual': True}
        for field in creation_fields:
            creation_data[field] = validated_data.get(field)
        technology = Technology.objects.create(**creation_data)
        for serializer, items in [
            (ManualVulnerabilitySerializer, validated_data.get('vulnerability')),
            (ManualExploitSerializer, validated_data.get('exploit'))
        ]:
            if not items:
                continue
            for item in items:
                field_data = item.copy()
                field_data['technology'] = technology
                serializer().create(field_data)
        return technology

    def get_findings(self, finding):
        return [finding] + list(finding.vulnerability.all()) + list(finding.exploit.all())


class ManualEndpointSerializer(ManualFindingModelSerializer):
    class Meta:
        model = Endpoint
        fields = ('id', 'enumeration', 'endpoint', 'status', 'task')
        extra_kwargs = {
            'enumeration': {'write_only': True},
            'task': {'write_only': True}
        }


class ManualEnumerationSerializer(ManualFindingModelSerializer):
    technology = ManualTechnologySerializer(read_only=False, many=True, required=False)
    endpoint = ManualEndpointSerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Enumeration
        fields = (
            'id', 'host', 'port', 'port_status', 'protocol', 'service', 'task',
            'technology', 'endpoint'
        )
        extra_kwargs = {
            'host': {'write_only': True},
            'task': {'write_only': True}
        }

    def create(self, validated_data):
        creation_fields = ['host', 'port', 'port_status', 'protocol', 'service', 'task']
        creation_data = {'is_manual': True}
        for field in creation_fields:
            creation_data[field] = validated_data.get(field)
        enumeration = Enumeration.objects.create(**creation_data)
        for serializer, items in [
            (ManualTechnologySerializer, validated_data.get('technology')),
            (ManualEndpointSerializer, validated_data.get('endpoint'))
        ]:
            if not items:
                continue
            for item in items:
                field_data = item.copy()
                field_data['enumeration'] = enumeration
                serializer().create(field_data)
        return enumeration

    def get_findings(self, finding):
        return [finding] + list(finding.technology.all()) + list(finding.endpoint.all())


class ManualHostSerializer(ManualFindingModelSerializer):
    enumeration = ManualEnumerationSerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Host
        fields = ('id', 'address', 'os_type', 'task', 'enumeration')
        extra_kwargs = {'task': {'write_only': True}}

    def create(self, validated_data):
        creation_fields = ['address', 'os_type', 'task']
        creation_data = {'is_manual': True}
        for field in creation_fields:
            creation_data[field] = validated_data.get(field)
        host = Host.objects.create(**creation_data)
        if validated_data.get('enumeration'):
            for e in validated_data.get('enumeration'):
                field_data = e.copy()
                field_data['host'] = host
                ManualEnumerationSerializer().create(field_data)
        return host

    def get_findings(self, finding):
        return [finding] + list(finding.enumeration.all())


class ManualCredentialSerializer(ManualFindingModelSerializer):
    class Meta:
        model = Credential
        fields = ('id', 'email', 'username', 'secret', 'task')
        extra_kwargs = {'task': {'write_only': True}}


class ManualOSINTSerializer(ManualFindingModelSerializer):
    class Meta:
        model = OSINT
        fields = ('id', 'data', 'data_type', 'source', 'task')
        extra_kwargs = {'task': {'write_only': True}}


class TaskSerializer(serializers.ModelSerializer):
    intensity_rank = IntensityField(source='intensity')
    osint = ManualOSINTSerializer(read_only=False, many=True, required=False)
    host = ManualHostSerializer(read_only=False, many=True, required=False)
    enumeration = ManualEnumerationSerializer(read_only=False, many=True, required=False)
    endpoint = ManualEndpointSerializer(read_only=False, many=True, required=False)
    technology = ManualTechnologySerializer(read_only=False, many=True, required=False)
    vulnerability = ManualVulnerabilitySerializer(read_only=False, many=True, required=False)
    credential = ManualCredentialSerializer(read_only=False, many=True, required=False)
    exploit = ManualExploitSerializer(read_only=False, many=True, required=False)

    class Meta:
        model = Task
        fields = (
            'id', 'target', 'process', 'tool', 'configuration',
            'intensity_rank', 'executor', 'status', 'scheduled_at',
            'scheduled_in', 'scheduled_time_unit', 'repeat_in',
            'repeat_time_unit', 'start', 'end', 'wordlists',
            'osint', 'host', 'enumeration', 'endpoint', 'technology',
            'vulnerability', 'credential', 'exploit', 'executions'
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
            ('osint', ManualOSINTSerializer), ('host', ManualHostSerializer),
            ('enumeration', ManualEnumerationSerializer), ('endpoint', ManualEndpointSerializer),
            ('technology', ManualTechnologySerializer),
            ('vulnerability', ManualVulnerabilitySerializer),
            ('credential', ManualCredentialSerializer), ('exploit', ManualExploitSerializer)
        ]
        for field, serializer in finding_fields:
            if validated_data.get(field):
                for item in validated_data.get(field):
                    field_data = item.copy()
                    field_data['task'] = task
                    finding = serializer().create(validated_data=field_data)
                    manual_findings.extend(serializer().get_findings(finding))
        # Resources are included as manual findings to make executions easier
        manual_findings.extend(list(task.wordlists.all()))
        domain = None
        if self.context.get('request'):
            domain = get_current_site(self.context.get('request')).domain
        producer(task, manual_findings, domain)
        return task
