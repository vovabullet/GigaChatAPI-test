#Получение токена ------------------------------------------------------------------------------------------------------
import json

import requests
import uuid
import urllib3

urllib3.disable_warnings() # скрыть InsecureRequestWarning

GigaChatKey = 'NTg0YTQ2YzYtNGM5Zi00YmYzLTg0MzUtOTNjYzE0YjdjNTc1OjBiNDNkNDhhLWNjMzMtNGM5ZS1hMWRhLTVjOTA3YTlmMjdkZg=='

rq_uid = str(uuid.uuid4())
#URL API, к которому мы обращаемся
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

#Данные для запроса
payload={
    'scope': 'GIGACHAT_API_PERS'
}
#Заголовки запроса
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': rq_uid,
    'Authorization': f'Basic {GigaChatKey}'
}

response = requests.request("POST", url, headers=headers, data=payload, verify=False) # verify=False Отключает проверку наличия сертификатов НУЦ Минцифры
giga_token = response.json()['access_token']

# Получение списка моделей ---------------------------------------------------------------------------------------------
url_models = "https://gigachat.devices.sberbank.ru/api/v1/models"
headers_models = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {giga_token}'
}

response_models = requests.get(url_models, headers=headers_models, verify=False)
models = [model['id'] for model in response_models.json()['data']]

print("Доступные модели GigaChat:", ', '.join(models))

# Тестирование температур ----------------------------------------------------------------------------------------------
import requests
import json

# Вопрос по теме кулинарных рецептов
user_question = "Напиши рецепт классического борща."

# Температуры для тестирования
temperatures = [0.1, 0.7, 1.7]

for temp in temperatures:
    print(f"\n\033[1mОтвет при temperature = {temp}\033[0m")
    print("―" * 50)

    payload = json.dumps({
        "model": "GigaChat",
        "messages": [{"role": "user", "content": user_question}],
        "temperature": temp,
        "top_p": 0.1,
        "n": 1,
        "max_tokens": 512
    })

    response = requests.post(
        "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers={'Authorization': f'Bearer {giga_token}', 'Content-Type': 'application/json'},
        data=payload,
        verify=False
    )

    answer = response.json()['choices'][0]['message']['content']
    print(answer)
    print("―" * 50)

# Настройки истории диалогов
message_history = []


def ask_gigachat(user_message, temperature=0.7):
    global message_history

    # Добавляем вопрос пользователя в историю
    message_history.append({"role": "user", "content": user_message})

    # Формируем запрос
    payload = json.dumps({
        "model": "GigaChat",
        "messages": message_history,
        "temperature": temperature,
        "max_tokens": 512
    })

    # Отправляем запрос
    response = requests.post(
        "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers={'Authorization': f'Bearer {giga_token}', 'Content-Type': 'application/json'},
        data=payload,
        verify=False
    )

    # Извлекаем и сохраняем ответ
    assistant_response = response.json()['choices'][0]['message']['content']
    message_history.append({"role": "assistant", "content": assistant_response})

    return assistant_response

# Пример использования
print(ask_gigachat("Привет! Как приготовить борщ?"))  # Первый вопрос
print(ask_gigachat("А вегетарианский вариант?"))  # Вопрос с учётом истории
print(ask_gigachat("Спасибо! А какие специи добавить?"))

# Генерация изображения ------------------------------------------------------------------------------------------------
from bs4 import BeautifulSoup
import re

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
payload = json.dumps({
    "model": "GigaChat",
    "messages": [
      {
         "role": "user",
         "content": "Нарисуй вкусный борщ"
      }
    ],
    "function_call": "auto"
  })

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {giga_token}'
  }

response = requests.request("POST", url, headers=headers, data=payload, verify=False)
answer = response.json()
answ = answer['choices'][0]['message']['content']
#images = re.findall(r'', answ)
src = BeautifulSoup(answ, 'html.parser').find('img').get('src')

url = f"https://gigachat.devices.sberbank.ru/api/v1/files/{src}/content"
payload={}
headers = {
    'Accept': 'application/jpg',
    'Authorization': f'Bearer {giga_token}'
  }

response = requests.request("GET", url, headers=headers, data=payload, verify=False)
with open(f"image.png", "wb") as img_file:
  img_file.write(response.content)