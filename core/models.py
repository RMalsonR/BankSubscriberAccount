from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from core.mixins import AbstractUUID
from core.enums import AccountStatusEnum


# TODO: may be should remove it to celery task flow
class BankAccountManager(models.Manager):
    """BankAccount model Manager. Using to select record with non zero hold"""
    def not_zero_hold(self):
        return self.filter(Q(hold__gt=0) & Q(status=AccountStatusEnum.OPEN.value)).select_for_update()


class BankAccount(AbstractUUID):
    """Subscriber account model."""

    owner_name = models.CharField(
        max_length=128,
        verbose_name='Account owner fullname'
    )
    balance = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=0,
        verbose_name='Account balance'
    )
    hold = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=0,
        verbose_name='Account hold bankroll (cash)',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(
        max_length=5,
        choices=AccountStatusEnum.as_choices(),
        verbose_name='Account status'
    )

    objects = BankAccountManager()

    def __str__(self):
        return f'{self.owner_name}: {self.status}'

    class Meta:
        verbose_name = 'Bank account'
        verbose_name_plural = 'Bank accounts'

