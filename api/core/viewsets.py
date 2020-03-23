from rest_framework.viewsets import GenericViewSet


class BaseGenericViewSet(GenericViewSet):
    actions_serializer_class = None
    actions_queryset = None

    def get_serializer_class(self):
        if self.actions_serializer_class is None:
            return super().get_serializer_class()

        serializer_class = self.actions_serializer_class.get(self.action)
        return serializer_class or super().get_serializer_class()

    def get_queryset(self):
        if self.actions_queryset is not None and self.action in self.actions_queryset.keys():
            return self.actions_queryset.get(self.action)
        return super().get_queryset()
