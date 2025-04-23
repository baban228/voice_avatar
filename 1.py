from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
import torch
import logging
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RussianChatBot:
    def __init__(self, model_name="deepseek-ai/deepseek-llm-7b-base"):
        """Инициализация модели DeepSeek"""
        try:
            set_seed(42)

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Используемое устройство: {self.device}")

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)

            logger.info(f"Модель {model_name} успешно загружена")

            # Паттерн для проверки русского языка
            self.russian_pattern = re.compile(r'[а-яА-ЯёЁ]+')

        except Exception as e:
            logger.error(f"Ошибка при загрузке модели: {e}")
            raise

    def is_russian(self, text, threshold=0.5):
        """Проверяет, является ли текст преимущественно русским"""
        if not text.strip():
            return False

        russian_chars = len(self.russian_pattern.findall(text))
        total_chars = max(len(re.findall(r'\w', text)), 1)
        return (russian_chars / total_chars) >= threshold

    def generate_response(self, user_input, max_length=150):
        """
        Генерирует ответ с помощью модели DeepSeek
        """
        try:
            prompt = f"Пользователь: {user_input}\nАссистент:"

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)

            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                top_k=50,
                top_p=0.9,
                repetition_penalty=1.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            bot_response = response[len(prompt):].strip()

            # Удаляем всё после первого законченного предложения
            bot_response = re.split(r'(?<=[.!?])\s', bot_response)[0]

            return bot_response

        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return "Извините, произошла ошибка при генерации ответа."

    def chat_loop(self):
        """Интерактивный режим чата"""
        print("Привет! Я умный ассистент на основе DeepSeek. Задавайте вопросы.")
        print("(Для выхода введите 'выход', 'exit' или 'quit')")

        while True:
            user_input = input("Вы: ")

            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("До свидания! Было приятно пообщаться.")
                break

            if not user_input.strip():
                print("Пожалуйста, введите сообщение.")
                continue

            response = self.generate_response(user_input)
            print(f"Ассистент: {response}")


if __name__ == "__main__":
    try:
        # Можно выбрать разные версии модели:
        # - "deepseek-ai/deepseek-llm-7b" (базовая)
        # - "deepseek-ai/deepseek-llm-67b" (более мощная)
        bot = RussianChatBot(model_name="deepseek-ai/deepseek-llm-7b-base")
        bot.chat_loop()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print("Произошла критическая ошибка. Приложение будет закрыто.")