import telebot
from setting import CAR_BOT_TOKEN


class TG_BOT:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)

    @staticmethod
    async def send_message_to_tg(message_text, chat_id):
        bot = telebot.TeleBot(CAR_BOT_TOKEN)
        bot.send_message(chat_id=chat_id, text=message_text, parse_mode='html', disable_web_page_preview=True)
