from rest_framework.viewsets import ModelViewSet


class BaseViewSet(ModelViewSet):
    ordering = ["-id"]
    # Required to remove PATCH method
    http_method_names = [
        "get",
        "post",
        "put",
        "delete",
    ]
