import logging

from django.db.transaction import atomic

from core.models import BankAccount

logger = logging.getLogger(__name__)


class SubtractHoldFlow(object):
    model = BankAccount

    def run(self):
        logger.debug('Start SubtractHoldFlow service.')
        with atomic():
            qs = self.model.objects.not_zero_hold()
            logger.debug(f'Select {len(qs)} records and lock them')
            for account in qs:
                account.balance -= account.hold
                account.hold = 0
                account.save()
            logger.debug('Finished SubtractHoldFlow service.')
