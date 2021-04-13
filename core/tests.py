import json
import uuid

from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase, APIRequestFactory

from .enums import BankAccountOperationsEnum
from .views import BankAccountViewSet
from .models import BankAccount
from .flows import SubtractHoldFlow


class BankAccountViewSetTestCase(APITestCase):
    """ApiTestCase for testing base BankAccountViewset actions."""
    response_template = {
        'status': status.HTTP_200_OK,
        'result': True,
        'addition': '',
        'description': {}
    }

    add_value_key = 'add_value'

    sub_value_key = 'sub_value'

    def setUp(self) -> None:
        """Setting up the test data and stuff: `factory`, `view`, `uris`"""
        self.model_1 = BankAccount.objects.create(
            owner_name='Петров Иван Сергеевич',
            balance=1700,
            hold=300,
            status='OPEN'
        )
        self.model_2 = BankAccount.objects.create(
            owner_name='Kazitsky Jason',
            balance=200,
            hold=200,
            status='OPEN'
        )
        self.model_3 = BankAccount.objects.create(
            owner_name='Пархоментко Антон Александрович',
            balance=10,
            hold=300,
            status='OPEN'
        )
        self.model_4 = BankAccount.objects.create(
            owner_name='Петечкин Петр Измаилович',
            balance=9999,
            hold=1,
            status='CLOSE'
        )
        self.factory = APIRequestFactory()
        self.base_uri = '/account/'
        self.view = None

    def factory_post(self, uri: str, data: dict, pk: uuid.uuid4):
        """Make POST request on uri path.
        :param uri: url path of action
        :param data: dict data for post
        :param pk: uuidV4 instance pk
        """
        request = self.factory.post(
            uri,
            data=json.dumps(data),
            content_type='application/json'
        )
        return self.view(request, pk=pk)

    def get_uri(self, action_path: str, account_id: uuid.uuid4) -> str:
        """Build uri for action.
        :param action_path: string, action path (`add`, `subtract`, `status`).
        :param account_id: uuidV4, account uuid.
        """
        return f'{self.base_uri}{account_id}/{action_path}/'

    def test_status_closed_validation_add(self):
        """Testing denied `add` operation in case of bank account status `CLOSE`"""
        model_uuid = self.model_4.id
        uri = self.get_uri('add', model_uuid)

        add_data = {
            self.add_value_key: 100
        }

        description = {
            "non_field_errors": [
                ErrorDetail(
                    string="You can't do anything with this account, because its status is `CLOSE`",
                    code='invalid'
                )
            ]
        }

        self.view = BankAccountViewSet.as_view(
            {
                'post': 'add'
            }
        )
        response = self.factory_post(uri, add_data, model_uuid)

        response_true = self.response_template
        response_true.update(
            {
                'status': status.HTTP_400_BAD_REQUEST,
                'result': False,
                'addition': BankAccountOperationsEnum.ADD.value,
                'description': description
            }
        )

        self.assertEqual(
            response_true,
            response.data,
            f'Excepted {response_true}, got {response.data} instead'
        )

    def test_status_closed_validation_sub(self):
        """Testing denied `subtract` operation in case of bank account status `CLOSE`"""
        model_uuid = self.model_4.id
        uri = self.get_uri('subtract', model_uuid)

        sub_data = {
            self.sub_value_key: 1
        }
        description = {
            "non_field_errors": [
                ErrorDetail(
                    string="You can't do anything with this account, because its status is `CLOSE`",
                    code='invalid'
                )
            ]
        }

        self.view = BankAccountViewSet.as_view(
            {
                'post': 'subtract'
            }
        )
        response = self.factory_post(uri, sub_data, model_uuid)

        response_true = self.response_template
        response_true.update(
            {
                'status': status.HTTP_400_BAD_REQUEST,
                'result': False,
                'addition': BankAccountOperationsEnum.SUB.value,
                'description': description
            }
        )

        self.assertEqual(
            response_true,
            response.data,
            f'Excepted {response_true}, got {response.data} instead'
        )

    def test_not_enough_money_sub(self):
        """Testing denied `subtract` operation in case of not enough money on bank account"""
        model_uuid = self.model_3.id
        uri = self.get_uri('subtract', model_uuid)

        sub_data = {
            self.sub_value_key: 100
        }
        description = {
            "non_field_errors": [
                ErrorDetail(
                    string="Don't have enough money for this operation",
                    code='invalid'
                )
            ]
        }

        self.view = BankAccountViewSet.as_view(
            {
                'post': 'subtract'
            }
        )
        response = self.factory_post(uri, sub_data, model_uuid)

        response_true = self.response_template
        response_true.update(
            {
                'status': status.HTTP_400_BAD_REQUEST,
                'result': False,
                'addition': BankAccountOperationsEnum.SUB.value,
                'description': description
            }
        )

        self.assertEqual(
            response_true,
            response.data,
            f'Excepted {response_true}, got {response.data} instead'
        )

    def test_correct_adding(self):
        """Testing correct `add` operation"""
        model_uuid = self.model_1.id
        uri = self.get_uri('add', model_uuid)

        add_data = {
            self.add_value_key: 100
        }

        self.view = BankAccountViewSet.as_view(
            {
                'post': 'add'
            }
        )
        response = self.factory_post(uri, add_data, model_uuid)

        response_true = self.response_template
        response_true.update(
            {
                'status': status.HTTP_200_OK,
                'result': True,
                'addition': BankAccountOperationsEnum.ADD.value,
            }
        )

        self.assertEqual(
            response_true,
            response.data,
            f'Excepted {response_true}, got {response.data} instead'
        )


class SubtractHoldFlowTestCase(TestCase):
    """Testcase class for testing Celery task flow."""
    default_assert_error_msg = 'SubtractHoldFlow working not correctly.\n' \
                               'Expected balance, hold: {true_balance}, {true_hold} \n' \
                               'Got: {balance}, {hold} instead.'

    def setUp(self) -> None:
        self.model_1 = BankAccount.objects.create(
            owner_name='Петров Иван Сергеевич',
            balance=1700,
            hold=300,
            status='OPEN'
        )
        self.model_2 = BankAccount.objects.create(
            owner_name='Kazitsky Jason',
            balance=200,
            hold=200,
            status='OPEN'
        )
        self.model_3 = BankAccount.objects.create(
            owner_name='Пархоментко Антон Александрович',
            balance=10,
            hold=300,
            status='OPEN'
        )
        self.model_4 = BankAccount.objects.create(
            owner_name='Петечкин Петр Измаилович',
            balance=9999,
            hold=1,
            status='CLOSE'
        )

    def update_models(self):
        """Get existing model again, for assert equal."""
        self.model_1 = BankAccount.objects.get(owner_name='Петров Иван Сергеевич')
        self.model_2 = BankAccount.objects.get(owner_name='Kazitsky Jason')
        self.model_3 = BankAccount.objects.get(owner_name='Пархоментко Антон Александрович')
        self.model_4 = BankAccount.objects.get(owner_name='Петечкин Петр Измаилович')

    def test_flow(self):
        """Testing flow"""
        flow = SubtractHoldFlow()
        flow.run()

        self.update_models()

        self.assertEqual(
            (1400, 0),
            (self.model_1.balance, self.model_1.hold),
            msg=self.default_assert_error_msg.format(
                    true_balance=1400,
                    true_hold=0,
                    balance=self.model_1.balance,
                    hold=self.model_1.hold
                )
        )

        self.assertEqual(
            (0, 0),
            (self.model_2.balance, self.model_2.hold),
            msg=self.default_assert_error_msg.format(
                true_balance=0,
                true_hold=0,
                balance=self.model_2.balance,
                hold=self.model_2.hold
            )
        )

        self.assertEqual(
            (-290, 0),
            (self.model_3.balance, self.model_3.hold),
            msg=self.default_assert_error_msg.format(
                true_balance=-290,
                true_hold=0,
                balance=self.model_3.balance,
                hold=self.model_3.hold
            )
        )

        self.assertEqual(
            (9999, 1),
            (self.model_4.balance, self.model_4.hold),
            msg=self.default_assert_error_msg.format(
                true_balance=9999,
                true_hold=1,
                balance=self.model_4.balance,
                hold=self.model_4.hold
            )
        )

