from telegram import Bot
from payment_control.payment_control.const import BOTTOKEN
from django.utils import timezone
from .models import Event

def send_telegram_notification(chat_id, message):
    # Замените 'YOUR_TOKEN' на токен вашего бота
    bot = Bot(token=BOTTOKEN)
    bot.sendMessage(chat_id=chat_id, text=message)


def send_event_notifications():
    print('set');
    # Получаем события, которые начнутся через день
    events = Event.objects.filter(start_time=timezone.now() + timedelta(days=1))
    # Отправляем уведомления для каждого события
    for event in events:
        message = f"Reminder: {event.title} starts tomorrow!"
        send_telegram_notification(chat_id='', message=message)