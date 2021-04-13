import logging

from celery.task import PeriodicTask
from celery.schedules import crontab

from .flows import SubtractHoldFlow

logger = logging.getLogger(__name__)


class SubtractHoldTask(PeriodicTask):
    """Subtract hold from balance every 10 minutes."""
    run_every = crontab(minute=10)

    def run(self, *args, **kwargs):
        logger.debug('Start Celery task: SubtractHoldTask')
        try:
            service = SubtractHoldFlow()
            service.run()
        except BaseException as e:
            logger.error(f'Get unexpected error during celery task: {e}')
        logger.debug('Finish Celery task: SubtractHoldTask')


