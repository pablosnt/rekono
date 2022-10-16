from typing import Generic

from rest_framework.mixins import (ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.viewsets import GenericViewSet

from settings.filters import SettingFilter
from settings.models import Setting
from settings.serializers import SettingSerializer

# Create your views here.


class SettingViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin):
    queryset = Setting.objects.all().order_by('-id')
    serializer_class = SettingSerializer
    filterset_class = SettingFilter
    search_fields = ['field']
    http_method_names = ['get', 'put']
