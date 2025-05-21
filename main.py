# Получение токена ------------------------------------------------------------------------------------------------------
import base64
from gigachat import GigaChat

# Проверка корректности ключей --------------------------------------------------------
GigaChatKey = 'NTg0YTQ2YzYtNGM5Zi00YmYzLTg0MzUtOTNjYzE0YjdjNTc1OmJlNDRkNjJlLTI4MjUtNDZkNi05ZGMzLTNkY2IyYTZkNzg5Nw=='

try:
    decoded = base64.b64decode(GigaChatKey).decode('utf-8')
    client_id, client_secret = decoded.split(':')
except Exception as e:
    print(f"Ошибка декодирования ключа: {e}")
    exit()

# авторизация через библиотеку ----------------------------------------------
giga = GigaChat(
        base_url="https://gigachat.devices.sberbank.ru/api/v1",
        credentials=GigaChatKey,  # Используем исходный base64-ключ напрямую
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )

# Без истории
first_response = giga.chat("Какие планеты входят в Солнечную систему?")
print("Ответ без истории:\n", first_response.choices[0].message.content)

# С сохранением истории
from gigachat.models import Chat, Messages

history = Chat(
    messages=[
        Messages(role="user", content="Какие планеты входят в Солнечную систему?"),
        Messages(role="assistant", content=first_response.choices[0].message.content),
        Messages(role="user", content="А какая самая большая?")
    ]
)
response = giga.chat(history)
print("\nОтвет с историей:\n", response.choices[0].message.content)

# Использование langchain_gigachat -----------------------------------------------------------------------------------
from langchain_gigachat import GigaChat as LangGigaChat
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import requests
import json
from bs4 import BeautifulSoup

# 1. Инициализация моделей
# Для langchain используем отдельный экземпляр с прямым указанием токена
langchain_llm = LangGigaChat(
    credentials=GigaChatKey,  # Используем исходный base64-ключ
    verify_ssl_certs=False
)

# 2. Работа с историей диалогов
try:
    # Без сохранения истории
    print("\nLangchain без истории:", langchain_llm.invoke("Какие планеты входят в Солнечную систему?"))

    # С сохранением истории
    memory = ConversationBufferMemory()
    conversation = ConversationChain(llm=langchain_llm, memory=memory)

    print("\nLangchain с историей 1:",
          conversation.invoke("Какие планеты входят в Солнечную систему?")['response'])
    print("Langchain с историей 2:",
          conversation.invoke("А какая самая большая?")['response'])

except Exception as e:
    print(f"Ошибка в langchain: {e}")


# 3. Диалог двух агентов -----------------------------------------------------------------------------------------------
def create_agent():
    return {
        'memory': ConversationBufferMemory(),
        'chain': ConversationChain(
            llm=LangGigaChat(
                credentials=GigaChatKey,  # Каждый агент со своим экземпляром
                verify_ssl_certs=False
            )
        )
    }


agent_a = create_agent()
agent_b = create_agent()

try:
    # Стартовый вопрос от агента A
    question = "Какие преимущества у Земли перед другими планетами солнечной системы?"
    response = agent_a['chain'].invoke(question)
    print("\nАгент A:", response['response'])

    # Агент B отвечает на последнее сообщение
    response = agent_b['chain'].invoke(response['response'])
    print("Агент B:", response['response'])

    # Продолжение диалога
    response = agent_a['chain'].invoke(response['response'])
    print("Агент A:", response['response'])

except Exception as e:
    print(f"Ошибка в диалоге агентов: {e}")

