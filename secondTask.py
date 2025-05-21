# Microsoft's Phi-3-mini-4k-instruct (через transformers) и Mistral-7B-Instruct-v0.2 (через llama-cpp-python)

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Отключаем предупреждение о симлинках
import os

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Инициализация модели
model_name = "microsoft/Phi-3-mini-4k-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype=torch.float16,
    pad_token_id=tokenizer.eos_token_id  # Решаем проблему с attention_mask
)

# Системная роль
system_prompt = """Ты - научный ассистент. Отвечай точно и кратко"""

history = [{"role": "system", "content": system_prompt}]


def generate_response(user_input):
    history.append({"role": "user", "content": user_input})

    # Форматирование с учетом шаблона диалога
    messages = [
        {"role": "system", "content": system_prompt},
        *history[1:]
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt",
        add_generation_prompt=True
    ).to(model.device)

    # Генерация с контролем вывода
    outputs = model.generate(
        inputs,
        max_new_tokens=400,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id
    )

    response = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
    history.append({"role": "assistant", "content": response})
    return response


# Пример диалога
print("Ответ 1:", generate_response("На какой ближайшей планете может быть жизнь?"))
print("Ответ 2:", generate_response("Почему мы до сих пор не исследовали её на предмет жизни?"))