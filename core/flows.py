import logging

from django.db.transaction import atomic

from core.models import BankAccount

logger = logging.getLogger(__name__)


class SubtractHoldFlow(object):
    model = BankAccount

    def run(self):
        logger.debug('Start SubtractHoldFlow service.')
        qs = self.model.objects.not_zero_hold()
        logger.debug(f'Select {len(qs)} records.')
        for account in qs:
            with atomic():
                account = BankAccount.objects.select_for_update().get(id=account.id)
                account.balance -= account.hold
                account.hold = 0
                account.save()
        logger.debug('Finished SubtractHoldFlow service.')
