from copy import deepcopy

from rest_framework import status
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.enums import BankAccountOperationsEnum
from core.mixins import GetSerializerClassMixin
from core.models import BankAccount
from core.serializers import (
    BankAccountForListSerializer,
    BankAccountForAddSerializer,
    BankAccountForSubtractSerializer,
    BankAccountForStatusSerializer
)


# TODO: May be shouldn't use ListModelMixin
class BankAccountViewSet(GetSerializerClassMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    """Bank account view set. Provided `default list` action
        and custom actions:
            add - adding cash to account balance
            subtract - adding subtract sum to account hold
            status - get account balance and status
    """
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountForListSerializer
    default_response_message = {
        'status': status.HTTP_200_OK,
        'result': True,
        'addition': '',
        'description': {}
    }
    serializer_action_classes = {
        'list': BankAccountForListSerializer,
        'add': BankAccountForAddSerializer,
        'subtract': BankAccountForSubtractSerializer,
        'status': BankAccountForStatusSerializer
    }

    def get_response_data(self, request: Request, operation: BankAccountOperationsEnum):
        """Return the default response message with filled addition"""
        resp = deepcopy(self.default_response_message)
        resp['addition'] = operation.value
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            resp['result'] = False
            resp['description'] = serializer.errors
            resp['status'] = status.HTTP_400_BAD_REQUEST
        else:
            resp['description'] = serializer.data
        return resp

    @action(
        methods=['post'],
        detail=True,
        url_path='add',
        serializer_class=BankAccountForAddSerializer
    )
    def add(self, request: Request, *args, **kwargs):
        resp_data = self.get_response_data(request, BankAccountOperationsEnum.ADD)
        return Response(data=resp_data, status=resp_data['status'])

    @action(
        methods=['post'],
        detail=True,
        url_path='subtract',
        serializer_class=BankAccountForSubtractSerializer
    )
    def subtract(self, request: Request, *args, **kwargs):
        resp_data = self.get_response_data(request, BankAccountOperationsEnum.SUB)
        return Response(data=resp_data, status=resp_data['status'])

    @action(
        methods=['get'],
        detail=True,
        url_path='status',
        serializer_class=BankAccountForStatusSerializer
    )
    def status(self, request: Request, *args, **kwargs):
        resp_data = self.get_response_data(request, BankAccountOperationsEnum.STATUS)
        return Response(data=resp_data, status=resp_data['status'])

