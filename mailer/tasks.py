from smtplib import SMTPException

from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger

from mailer.engine import send_all, retry_deferred as mailer_engine_retry_deferred
from mailer.exceptions import TimeoutError

logger = get_task_logger(__name__)

DEFAULT_LIMIT = getattr(settings, 'MAILER_DEFAULT_LIMIT', None)
DEFAULT_TIMEOUT = getattr(settings, 'MAILER_DEFAULT_TIMEOUT', None)

@shared_task(throws=(TimeoutError, SMTPException))
def send_mail():
    send_all(limit=DEFAULT_LIMIT, timeout=DEFAULT_TIMEOUT)

@shared_task
def retry_deferred():
    mailer_engine_retry_deferred()
