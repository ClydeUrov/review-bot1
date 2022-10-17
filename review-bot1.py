import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv


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
    load_dotenv()
    logging.warning('Бот запущен1')
    timestamp = time.time()
    bot = telegram.Bot(token=os.environ["TG_TOKEN"])
    while True:
        try:
            headers = {"Authorization": f"Token {os.environ['DEVMAN_TOKEN']}"}
            params = {"timestamp": timestamp, "timeout": 0.001}
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
            logging.warning('Бот запущен')
        except requests.ConnectionError:
            time.sleep(30)


if __name__ == "__main__":
    main()
