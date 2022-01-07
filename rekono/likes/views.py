from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

# Create your views here.


class LikeManagementView(GenericViewSet):

    def get_queryset(self):
        return super().get_queryset().annotate(likes_count=Count('liked_by'))

    @extend_schema(request=None, responses={201: None})
    @action(detail=True, methods=['POST'], url_path='like', url_name='like', permission_classes=[IsAuthenticated])
    def like(self, request, pk):
        instance = self.get_object()
        instance.liked_by.add(request.user)
        instance.save()
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=['POST'], url_path='dislike', url_name='dislike', permission_classes=[IsAuthenticated])
    def dislike(self, request, pk):
        instance = self.get_object()
        user = request.user
        instance.liked_by.remove(user)
        instance.save()
        getattr(user, f'liked_{instance.__class__.__name__.lower()}').remove(instance)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
