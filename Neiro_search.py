from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import logging
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neiro_search:
    def __init__(self, model_name="sberbank-ai/rugpt3medium_based_on_gpt2"):
        """Инициализация русскоязычной модели"""
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Используемое устройство: {self.device}")

            # Загружаем модель и токенизатор
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)

            logger.info(f"Модель {model_name} успешно загружена")

            # Паттерн для проверки русского языка
            self.russian_pattern = re.compile(r'[а-яА-ЯёЁ]+')

        except Exception as e:
            logger.error(f"Ошибка при загрузке модели: {e}")
            raise

    def generate_response(self, user_input, max_length=100):
        """Генерация ответа на русском языке"""
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
            return response[len(prompt):].strip()

        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."

    def chat_loop(self):
        """Интерактивный режим чата"""
        print("Привет! Я русскоязычный ассистент. Задавайте вопросы.")
        print("(Для выхода введите 'выход', 'exit' или 'quit')")

        while True:
            user_input = input("Вы: ")

            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("До свидания!")
                break

            if not user_input.strip():
                print("Пожалуйста, введите сообщение.")
                continue

            response = self.generate_response(user_input)
            print(f"Ассистент: {response}")


if __name__ == "__main__":
    try:
        # Доступные русскоязычные модели:
        # - "sberbank-ai/rugpt3small_based_on_gpt2" (лёгкая)
        # - "sberbank-ai/rugpt3medium_based_on_gpt2" (рекомендуемая)
        # - "sberbank-ai/rugpt3large_based_on_gpt2" (требует больше ресурсов)

        bot = Neiro_search(model_name="sberbank-ai/rugpt3small_based_on_gpt2")
        bot.chat_loop()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print("Произошла критическая ошибка. Приложение будет закрыто.")