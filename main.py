import pyttsx3  # синтез речи (Text-To-Speech)
from vosk import Model, KaldiRecognizer
import queue
import pyaudio
import time


from commands import *
from settings_assistant import VoiceAssistant

# Инициализация глобальных переменных
assistant = VoiceAssistant()
ttsEngine = pyttsx3.init()

def setup_assistant_voice():
    """
    Установка голоса по умолчанию (индекс может меняться в
    зависимости от настроек операционной системы)
    """
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            # Microsoft Zira Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[1].id)
        else:
            # Microsoft David Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[2].id)
    else:
        assistant.recognition_language = "ru-RU"
        # Microsoft Irina Desktop - Russian
        ttsEngine.setProperty("voice", voices[0].id)

def initialize_vosk_recognition():
    """
    Инициализация ресурсов для офлайн-распознавания речи
    """
    try:
        # Загрузка модели Vosk
        model = Model("models/vosk-model-small-ru-0.22")

        # Инициализация PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()

        # Инициализация распознавателя Vosk
        offline_recognizer = KaldiRecognizer(model, 16000)

        return stream, offline_recognizer, p
    except Exception as e:
        print(f"Произошла ошибка при инициализации: {e}")
        return None, None, None

def listen_and_recognize(stream, offline_recognizer, command_queue, activation_lock, active_until):
    """
    Прослушивание и распознавание речи
    :param stream: аудиопоток
    :param offline_recognizer: распознаватель Vosk
    :param command_queue: очередь для передачи команд
    :param activation_lock: блокировка для синхронизации доступа к активации
    :param active_until: время окончания активности
    """
    try:
        commands.play_voice_assistant_speech("Низкобюджетная версия алисы готова к работе...")
        commands.play_voice_assistant_speech("чтобы узнать функционал скажите слово инструкция")
        print("Слушаю...")
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                break
            if offline_recognizer.AcceptWaveform(data):
                result = offline_recognizer.Result()
                result = json.loads(result)
                recognized_data = result["text"].strip().lower()
                if recognized_data:
                    print(f"Распознано: {recognized_data}")
                    with activation_lock:
                        if not active_until[0]:
                            if "инструкция" in recognized_data:
                                file_path = 'instruction.html'
                                # Открытие файла в браузере
                                webbrowser.open(file_path)
                                commands.play_voice_assistant_speech("готово")
                            # Проверка наличия слова-ключа "алиса"
                            if "алиса" in recognized_data:
                                active_until[0] = time.time() + 60  # Активность в течение 1 минуты
                                commands.play_voice_assistant_speech("Слушаю...")
                        else:
                            # Проверка времени активности
                            if time.time() < active_until[0]:
                                # Отделение команды от дополнительной информации (аргументов)
                                voice_input = recognized_data.split(" ")
                                if len(voice_input) > 0:
                                    command = voice_input[0]
                                    arguments = " ".join(voice_input[1:]) if len(voice_input) > 1 else ""
                                    # Помещаем команду и аргументы в очередь для обработки в основном потоке
                                    command_queue.put((command, arguments))
                            else:
                                active_until[0] = None
                                print("Активность завершена")
    except Exception as e:
        print(f"Произошла ошибка при распознавании: {e}")

def process_queue(commands, command_queue):
    while not command_queue.empty():
        command, arguments = command_queue.get()
        print(f"Выполняю команду: {command} с аргументами: {arguments}")
        commands.execute_command(command, arguments)
    commands.avatar.after(100, process_queue, commands, command_queue)  # Проверяем очередь каждые 100 мс

def main():
    # настройка данных голосового помощника
    assistant.name = "Alice"
    assistant.sex = "female"
    assistant.speech_language = "ru"

    # инициализация инструмента синтеза речи
    setup_assistant_voice()

    # Инициализация ресурсов для офлайн-распознавания речи
    stream, offline_recognizer, p = initialize_vosk_recognition()
    if stream is None or offline_recognizer is None or p is None:
        print("Не удалось инициализировать ресурсы для распознавания речи")
        return

    # Создание объекта Commands
    global commands
    commands = Commands()
    commands.load_commands('commands.json')
    commands.set_ttsEngine(ttsEngine)

    # Создание очереди для передачи команд
    command_queue = queue.Queue()

    # Блокировка для синхронизации доступа к активации и время окончания активности
    activation_lock = threading.Lock()
    active_until = [None]

    # Создание и запуск потока для обработки голосовых команд
    voice_thread = threading.Thread(
        target=listen_and_recognize,
        args=(stream, offline_recognizer, command_queue, activation_lock, active_until),
        daemon=True
    )
    voice_thread.start()

    # Запуск обработчика очереди
    commands.avatar.after(100, process_queue, commands, command_queue)

    # Запуск главного цикла Tkinter
    try:
        commands.avatar.mainloop()
    finally:
        # Завершение работы аудиопотока
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()