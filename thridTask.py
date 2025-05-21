from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import os

# Скачивание модели (выполнить один раз)
model_path = hf_hub_download(
    repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
    filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    local_dir="models",
    resume_download=True
)

# Инициализация
llm = Llama(
    model_path=model_path,
    n_ctx=2048,
    n_gpu_layers=30,
    verbose=False
)

# Диалоговая система
history = [
    {"role": "system", "content": "Ты - научный ассистент. Отвечай точно и кратко"}
]


def mistral_query(question):
    history.append({"role": "user", "content": question})

    response = llm.create_chat_completion(
        messages=history,
        temperature=0.6,
        max_tokens=300,
        stop=["</s>"]
    )

    answer = response['choices'][0]['message']['content']
    history.append({"role": "assistant", "content": answer})
    return answer


# Пример использования
print("Mistral ответ:", mistral_query("Сколько градусов на поверхности солнца?"))
print("Mistral ответ:", mistral_query("На сколько близко мы можем к нему подобраться?"))