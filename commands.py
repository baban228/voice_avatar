import json
import threading
import requests
import configparser
import random

from Avatar import Avatar


class Commands:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini')
        self.api_key = self.config.get('Weather', 'WEATHER_API')
        self.city = self.config.get('Weather', 'CITY')

        self.file_path = 'jokes.txt'

        self.commands = None
        self.ttsEngine = None

        self.state = "default"

        self.avatar = Avatar()
        self.avatar_thread = threading.Thread(target=self.avatar.mainloop, daemon=True)
        self.avatar_thread.start()

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
                    self.change_state("anger")
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
                elif action == 'set_reminder':
                    self.set_reminder(arguments)
                elif action == 'play_music':
                    self.play_music(arguments)
                elif action == 'check_calendar':
                    self.check_calendar(arguments)
                elif action == 'get_day_of_week':
                    self.get_day_of_week(arguments)
                else:
                    print("Неизвестное действие")
                return
        print("Команда не найдена")

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
        except FileNotFoundError:
            return "Файл не найден"
        except Exception as e:
            return f"Произошла ошибка: {e}"

    def set_reminder(self, arguments):
        self.play_voice_assistant_speech(f"Установлен напоминание: {arguments}")

    def play_music(self, arguments):
        self.play_voice_assistant_speech(f"Воспроизведение музыки: {arguments}")

    def check_calendar(self, arguments):
        self.play_voice_assistant_speech(f"Проверка календаря: {arguments}")

    def get_day_of_week(self, arguments):
        self.play_voice_assistant_speech(f"День недели: {arguments}")