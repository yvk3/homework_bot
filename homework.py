import telegram
import requests
import time
import logging
import os

from dotenv import load_dotenv

load_dotenv()


CONNECTION_ERROR = '{error}, {url}, {headers}, {params}'
WRONG_ENDPOINT = '{response_status}, {url}, {headers}, {params}'
WRONG_HOMEWORK_STATUS = '{homework_status}'
WRONG_DATE_TYPE = 'Неверный тип данных {type}, вместо "dict"'
STATUS_IS_CHANGED = '{verdict}, {homework}'
STATUS_IS_NOT_CHANGED = 'Статус не изменился, нет новых записей.'
FAILURE_TO_SEND_MESSAGE = '{error}, {message}'
GLOBAL_VARIABLE_IS_MISSING = 'Отсутствует глобальная переменная'
GLOBAL_VARIABLE_IS_EMPTY = 'Нет значения у глобальной переменной'
MESSAGE_IS_SENT = 'Сообщение {message} отправлено'
FORMAT_NOT_JSON = 'Ответ не в формате json {error}'

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filename='homework_log.log',
    filemode='w',
    encoding='utf-8',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(
    logging.StreamHandler()
)


class ServiceError(Exception):
    """Ошибка, нет доступа к заданноу эндпоинту."""


class NetworkError(Exception):
    """Ошибка, отсутствует сеть."""


class EndpointError(Exception):
    """Ошибка, эндпоинте не корректен."""


class MessageSendingError(Exception):
    """Ошибка отправки сообщения."""


class DataTypeError(Exception):
    """Ошибка, тип данных не dict."""


class GlobalsError(Exception):
    """Ошибка, проверить глобальные переменные."""


class ResponseFormatError(Exception):
    """Ошибка, ответ от эндпоинт не в формате json."""


def check_tokens():
    """Проверяется наличие переменных окружения (токены) для работы бота."""
    for key in (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, ENDPOINT):
        if key is None:
            logging.critical(GLOBAL_VARIABLE_IS_MISSING)
            return False
        if not key:
            logging.critical(GLOBAL_VARIABLE_IS_EMPTY)
            return False
    return True


def send_message(bot, message):
    """Студенту отправляется сообщение в Телеграм, о статусе его работы."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(
            f'Сообщение отправлено: {message}'
        )
    except Exception as error:
        logging.error(f"Ошибка отправки запроса статуса: {error}")


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API-сервса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    all_parms = dict(headers=HEADERS, params=params, url=ENDPOINT)
    try:
        response = requests.get(**all_parms)
    except requests.exceptions.RequestException as error:
        raise telegram.TelegramError(CONNECTION_ERROR.format(
            error=error,
            **all_parms,
        ))
    response_status = response.status_code
    if response_status != 200:
        raise EndpointError(WRONG_ENDPOINT.format(
            response_status=response_status,
            **all_parms,
        ))
    try:
        return response.json()
    except Exception as error:
        raise ResponseFormatError(FORMAT_NOT_JSON.format(error))


def check_response(response):
    """Проверяется ответ API.
        Должен вернуться номер
    домашней работы, если работа была отправлена.
    """
    if isinstance(response, dict):
        if 'homeworks' in response:
            if isinstance(response.get('homeworks'), list):
                return response.get('homeworks')[0]
            raise TypeError('API возвращает не список.')
        raise KeyError('В ответе нет ключа homeworks.')
    raise TypeError('API возвращает не словарь.')


def parse_status(homework):
    """Какой статус у проверяемой домашней работы."""
    if not isinstance(homework, dict):
        raise DataTypeError(WRONG_DATE_TYPE.format(type(homework)))
    if 'homework_name' not in homework:
        raise KeyError('Такой работы нет')
    homework_status = homework.get('status')
    homework_name = homework.get('homework_name')

    if homework_status not in HOMEWORK_VERDICTS:
        raise NameError(WRONG_HOMEWORK_STATUS.format(homework_status))

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise GlobalsError('Ошибка глобальных переменных.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)
            logging.info(homework)
            current_timestamp = response.get('current_date')
        except IndexError:
            message = 'Статус домашней работы не изменился.'
            send_message(bot, message)
            logging.info(message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)
        logging.info(MESSAGE_IS_SENT.format(message))


if __name__ == '__main__':
    main()
