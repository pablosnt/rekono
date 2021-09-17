from processes.models import Process
from processes.serializers import ProcessSerializer
from rest_framework.viewsets import ModelViewSet

# Create your views here.


class ProcessViewSet(ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
