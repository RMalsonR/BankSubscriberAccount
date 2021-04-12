import uuid

from django.db import models


class AbstractUUID(models.Model):
    """Abstract model to override id (pk) by UUIDv4."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='User uuid')

    class Meta:
        abstract = True


class GetSerializerClassMixin:
    def get_serializer_class(self):
        """
        A class which inhertis this mixins should have variable
        `serializer_action_classes`.
        Look for serializer class in self.serializer_action_classes, which
        should be a dict mapping action name (key) to serializer class (value),
        i.e.:
        class SampleViewSet(viewsets.ViewSet):
            serializer_class = SampleSerializer
            serializer_action_classes = {
               'list': SampleListSerializer,
               'retrieve': SampleRetrieveSerializer,
            }
            @action
            def list:
                ...
        If there's no entry for that action then just fallback to the regular
        get_serializer_class lookup: self.serializer_class, DefaultSerializer.
        """
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
