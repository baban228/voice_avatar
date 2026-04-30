import json
import threading
import requests
import configparser
import random
import webbrowser
from datetime import datetime
import os

from Avatar import Avatar
from Neiro_search import Neiro_search

class Commands:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini')
        self.api_key = self.config.get('Weather', 'WEATHER_API')
        self.city = self.config.get('Weather', 'CITY')

        self.file_path = 'jokes.txt'

        self.commands = None
        self.ttsEngine = None

        self.holidays = [
            (1, 1, "Новый год"),
            (7, 1, "Рождество Крещатика"),
            (8, 3, "Международный женский день"),
            (9, 5, "День Весны и Труда"),
            (12, 6, "День России"),
            (24, 12, "Рождество"),
            # Добавьте другие праздники по необходимости
        ]

        self.state = "default"
        self.states = ["default", "anger", "move_right_arm", "jump"]

        self.avatar = Avatar()
        self.avatar_thread = threading.Thread(target=self.avatar.mainloop, daemon=True)
        self.avatar_thread.start()

        self.neiro_search = Neiro_search()
        self.file_path = 'instruction.html'

    def change_state(self, new_state):
        print(f"изменилось с {self.state} на {new_state}")
        self.state = new_state
        self.activate_functions()

    def activate_functions(self):
        if self.state == "default":
            self.avatar.set_animation("default")
        elif self.state == "anger":
            self.avatar.set_animation("anger")
        elif self.state == "move_right_arm":
            self.avatar.set_animation("move_right_arm")
        elif self.state == "jump":
            self.avatar.set_animation("jump")
        else:
            print("Unknown state")

    def set_ttsEngine(self, ttsEngine):
        self.ttsEngine = ttsEngine

    def load_commands(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.commands = data['commands']

    def execute_command(self, command_name, arguments):
        for command in self.commands:
            if command['name'] == command_name:
                action = command['action']
                if action == 'greet':
                    self.greet()
                elif action == "get_time":
                    self.get_time()
                elif action == 'get_weather':
                    self.get_weather()
                elif action == 'change_state':
                    new_state = command.get('state')
                    if new_state:
                        self.change_state(new_state)
                    else:
                        print("Не указано новое состояние для команды 'change_state'")
                elif action == 'tell_joke':
                    self.tell_joke()
                elif action == 'create_node':
                    self.create_node(arguments)
                elif action == "display_notes_in_default_editor":
                    self.display_notes_in_default_editor()
                elif action == 'play_music':
                    self.play_music(arguments)
                elif action == 'check_calendar':
                    self.check_calendar()
                elif action == 'display_current_weekday':
                    self.display_current_weekday()
                elif action == 'instruction':
                    self.instruction()
                elif action == 'exit':
                    self.exit_program(arguments)
                else:
                    print("Неизвестное действие")
                return
        self.play_voice_assistant_speech(self.neiro_search.answer(command_name + arguments))
        print(self.neiro_search.answer(command_name + arguments))
        self.change_state(random.choice(self.states))

    def play_voice_assistant_speech(self, text_to_speech):
        """
        Проигрывание речи ответов голосового ассистента (без сохранения аудио)
        :param text_to_speech: текст, который нужно преобразовать в речь
        """
        if self.ttsEngine:
            self.ttsEngine.say(str(text_to_speech))
            self.ttsEngine.runAndWait()
        else:
            print(f"Текст: {text_to_speech}")

    def greet(self):
        self.play_voice_assistant_speech("Привет! Как я могу помочь?")
        self.change_state(random.choice(self.states))

    def get_time(self):
        """
        Возвращает текущее время в формате 'ЧЧ:ММ:СС'.
        """
        now = datetime.now()
        self.play_voice_assistant_speech(now.strftime("%H:%M:%S"))
        self.change_state("default")

    def get_weather(self, lang='ru'):
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}appid={self.api_key}&q={self.city}&units=metric&lang={lang}"

        response = requests.get(complete_url)
        weather_data = response.json()

        if weather_data['cod'] == 200:
            main = weather_data['main']
            temperature = main['temp']
            pressure = main['pressure']
            humidity = main['humidity']
            weather_description = weather_data['weather'][0]['description']

            self.play_voice_assistant_speech(f"Температура: {temperature}°C\n"
                                             f"Давление: {pressure} гПа\n"
                                             f"Влажность: {humidity}%\n"
                                             f"Описание: {weather_description}")
            self.change_state("jump")
        elif weather_data['cod'] == 404:
            self.play_voice_assistant_speech("Город не найден")
        else:
            print("Полный ответ API:", weather_data)
            return f"Ошибка: {weather_data.get('message', 'Неизвестная ошибка')}"

    def tell_joke(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if not lines:
                    self.play_voice_assistant_speech("Похоже сегодня без анекдотов")
                    self.change_state("move_right_arm")
                self.play_voice_assistant_speech(random.choice(lines).strip())
                self.change_state("move_right_arm")
        except FileNotFoundError:
            return "Файл не найден"
        except Exception as e:
            return f"Произошла ошибка: {e}"

    def create_node(self, arguments):
        """
            Функция для создания заметки и сохранения ее в файл.

            :param note: Текст заметки.
            """
        with open("notes.txt", "a", encoding="utf-8") as file:
            file.write(arguments + "\n")
        print(f"Заметка добавлена: {arguments}")
        self.play_voice_assistant_speech(f"Заметка добавлена: {arguments}")
        self.change_state("jump")

    def display_notes_in_default_editor(self):
        """
        Функция для отображения всех заметок в стандартном текстовом редакторе.
        """
        try:
            # Открываем файл в стандартном текстовом редакторе
            webbrowser.open("notes.txt")
        except Exception as e:
            print(f"Не удалось открыть файл: {e}")


    def play_music(self, arguments):
        self.play_voice_assistant_speech(f"Воспроизведение музыки: {arguments}")
        self.change_state("move_right_arm")

    def get_holiday(self, holidays):
        """
        Функция для получения ближайшего праздника из списка.

        :param holidays: Список праздников в формате (день, месяц, название праздника).
        :return: Название ближайшего праздника и дата.
        """
        today = datetime.today()
        current_year = today.year

        nearest_holiday = None
        nearest_date = None

        for day, month, name in holidays:
            holiday_date = datetime(current_year, month, day)

            # Если праздник уже прошел в этом году, рассмотрим следующий год
            if holiday_date < today:
                holiday_date = datetime(current_year + 1, month, day)

            if nearest_holiday is None or holiday_date < nearest_date:
                nearest_holiday = name
                nearest_date = holiday_date

        days_until_holiday = (nearest_date - today).days
        return nearest_holiday, nearest_date, days_until_holiday

    def check_calendar(self):
        """
        Функция для отображения ближайшего праздника.
        """
        nearest_holiday, nearest_date, days_until_holiday = self.get_holiday(self.holidays)
        formatted_date = nearest_date.strftime("%d.%m.%Y")
        self.play_voice_assistant_speech(f"Ближайший праздник: {nearest_holiday} ({formatted_date})")
        self.play_voice_assistant_speech(f"До праздника осталось: {days_until_holiday} дней")
        self.change_state("default")


    def get_day_of_week(self):
        """
        Функция для получения названия текущего дня недели на русском языке.

        :return: Название текущего дня недели на русском языке.
        """
        # Словарь для перевода номера дня недели в название на русском языке
        weekdays = {
            0: "понедельник",
            1: "вторник",
            2: "среда",
            3: "четверг",
            4: "пятница",
            5: "суббота",
            6: "воскресенье"
        }

        # Получаем текущую дату
        today = datetime.today()

        # Получаем номер дня недели (0 - понедельник, 6 - воскресенье)
        weekday_number = today.weekday()

        # Возвращаем название дня недели на русском языке
        return weekdays.get(weekday_number, "Неверная дата")

    def display_current_weekday(self):
        """
        Функция для отображения названия текущего дня недели.
        """
        weekday_name = self.get_day_of_week()
        self.play_voice_assistant_speech(f"Сегодня {weekday_name}")
        self.change_state("agree")
    def instruction(self):
        webbrowser.open(self.file_path)
        self.play_voice_assistant_speech("готово")
    def exit_program(self, arguments):
        if "бездушная машина" in arguments:
            self.play_voice_assistant_speech("айл би бэк")
            os._exit(0)
        else:
            self.play_voice_assistant_speech("бай бай")
            os._exit(0)