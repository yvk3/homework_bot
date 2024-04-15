# Телеграмм бот для получения статуса проверки домашнего задания - homework_bot

Написать Telegram-bot, который через API сервис Практикума.Домашка будет сообщать о статуса домашней работы.
Статусы проверки работы:
- работа принята на проверку;
- работа возвращена для исправления ошибок;
- работа принята.

## Технологии

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Telegram](https://img.shields.io/badge/telegram-28A4E4?style=for-the-badge&logo=telegram&logoColor=white&labelColor=28A4E4)
- [Python 3.9](https://www.python.org/downloads/)

## Установка проекта локально:
***- Клонируйте репозиторий:***
```
git@github.com:yvk3/homework_bot.git
```

***- Установите и активируйте виртуальное окружение:***
- для MacOS/Linux
```
python3 -m venv venv
source env/bin/activate
```
- для Windows
```
python -m venv venv
source venv/Scripts/activate
```

***- Установите зависимости из файла requirements.txt:***
```
python -m pip install --upgrade pip
cd backend
pip install -r requirements.txt
```

***- Запуск бота***
```python
python homework.py
```
