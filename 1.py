import requests


def get_weather(api_key, city, lang='ru'):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city}&units=metric&lang={lang}"

    response = requests.get(complete_url)
    weather_data = response.json()

    if weather_data['cod'] == 200:
        main = weather_data['main']
        temperature = main['temp']
        pressure = main['pressure']
        humidity = main['humidity']
        weather_description = weather_data['weather'][0]['description']

        return (f"Температура: {temperature}°C\n"
                f"Давление: {pressure} гПа\n"
                f"Влажность: {humidity}%\n"
                f"Описание: {weather_description}")
    elif weather_data['cod'] == 404:
        return "Город не найден"
    else:
        print("Полный ответ API:", weather_data)
        return f"Ошибка: {weather_data.get('message', 'Неизвестная ошибка')}"


# Пример использования функции
api_key = 'a576597d187e2488dc90e27fabd1f2df'  # Замените на ваш API ключ
city = 'Москва'
print(get_weather(api_key, city))