# Импорт зависимостей
import json

from ollama import Client

from api_token import API_TOKEN
from history_manager import HistoryManager
from language_manager import LanguageManager
from prompt_manager import PromptManager

# Создаем клиент
client = Client(
    host='https://ollama.com',
    headers={'Authorization': 'Bearer ' + API_TOKEN}
)


# Создаем функцию получения ответа от нейросети
def get_ai_response(prompt: str, lang: str) -> str:
    try:
        model = 'gpt-oss:20b-cloud'
        history_manager = HistoryManager()
        language_manager = LanguageManager()
        prompt_manager = PromptManager()

        system_prompts = language_manager.translate_prompts(lang)

        chat_id = history_manager.chat_manager.current_chat_id
        custom_prompt = prompt_manager.get_prompt(chat_id)

        chat_history = history_manager.get_history()
        chat_history.append({'role': 'user', 'content': prompt})
        if not chat_history:
            chat_history = [{'role': 'user', 'content': prompt}]

        messages = [
            {'role': 'system', 'content': system_prompts[0]},
            {'role': 'system', 'content': system_prompts[1]},
            {'role': 'system', 'content': system_prompts[2]},
            {'role': 'system', 'content': system_prompts[3]}
        ]

        if custom_prompt:
            messages.append({'role': 'system', 'content': f'[ДОПОЛНИТЕЛЬНАЯ ИНСТРУКЦИЯ ПОЛЬЗОВАТЕЛЯ]: {custom_prompt}'})

        messages.extend(chat_history)

        response = client.chat(
            model=model,
            messages=messages
        )

        return response['message']['content']
    except:
        return False
