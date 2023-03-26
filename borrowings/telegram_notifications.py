import telegram
from django.conf import settings


async def send_telegram_notification(message: str) -> None:
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
