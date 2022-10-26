import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logger = logging.getLogger("Logger")


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_text(attempt):
    lesson_title = attempt["lesson_title"]
    lesson_url = attempt["lesson_url"]
    if attempt["is_negative"]:
        text = f"""У вас проверили работу "{lesson_title}"\n
        \nВ работе нашлись ошибки.\n{lesson_url}"""
    else:
        text = f"""У вас проверили работу "{lesson_title}"\n
        \nПреподавателю всё понравилось, можно приступать к
        следующему уроку!\n{lesson_url}"""
    return text


def main():
    timestamp = time.time()
    load_dotenv()
    bot = telegram.Bot(token=os.environ["TG_TOKEN"])
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot, os.environ["TG_CHAT_ID"]))
    logger.info("Бот запущен")
    while True:
        try:
            headers = {"Authorization": f"Token {os.environ['DEVMAN_TOKEN']}"}
            params = {"timestamp": timestamp, "timeout": 10}
            response = requests.get(
                "https://dvmn.org/api/long_polling/", headers=headers, params=params
            )
            response.raise_for_status()
            answer = response.json()
            if answer["status"] == "found":
                timestamp = answer["last_attempt_timestamp"]
                new_attempt = answer["new_attempts"][0]
                bot.send_message(
                    chat_id=os.environ["TG_CHAT_ID"], text=get_text(new_attempt)
                )
            elif answer["status"] == "timeout":
                timestamp = answer["timestamp_to_request"]
        except requests.exceptions.ReadTimeout:
            pass
        except requests.ConnectionError:
            time.sleep(30)
        except Exception as err:
            logger.warning("Бот упал с ошибкой:")
            logger.warning(err, exc_info=True)

if __name__ == "__main__":
    main()
