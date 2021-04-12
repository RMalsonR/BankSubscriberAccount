import logging

from django.db.models import Model

from core.models import BankAccount

logger = logging.getLogger(__name__)


class SubtractHoldFlow(object):
    model = BankAccount

    def __init__(self, batch_size: int):
        self.batch_size = batch_size

    def run(self):
        logger.debug('Start SubtractHoldFlow service.')
        qs = self.model.objects.not_zero_hold
        logger.debug(f'Select {len(qs)} records')
        for account in qs:
            account.balance -= account.hold
            account.hold = 0
        logger.debug(f'Start updating record.')
        self.model.objects.bulk_update(
            qs,
            ['balance', 'hold'],
            batch_size=self.batch_size
        )
        logger.debug('Finished SubtractHoldFlow service.')
