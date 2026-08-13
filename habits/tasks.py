from django.utils import timezone

from celery import shared_task
from celery.utils.log import get_task_logger

from habits.services import send_telegram_notification

logger = get_task_logger(__name__)


@shared_task
def remind_habit():
    chat_id = "@RychardFamichou"
    text = "Пить воду"
    now = timezone.localtime(timezone.now())

    if now.hour in (6, 12, 18):
        send_telegram_notification(chat_id, text)

    logger.info("!!! СРАБОТАЛА ЗАДАЧА REMIND_HABIT !!!")
    return "Успешно выполнено!"
