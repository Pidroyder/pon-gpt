# Импорт зависимостей
import os
import json
from datetime import datetime

from kivy.utils import platform

if platform == 'android':
    try:
        from android.storage import app_storage_path
    except:
        app_storage_path = None
else:
    app_storage_path = None


# Создание класса управления промптами
class PromptManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PromptManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, prompts_file='prompts.json'):
        if self._initialized:
            return
        self._initialized = True
        self.prompts_file = prompts_file
        self.prompts = {}
        self._load_prompts()

    def _get_file_path(self) -> str:
        '''Получает путь к файлу с промптами'''
        if platform == 'android':
            return os.path.join(app_storage_path(), self.prompts_file)
        else:
            return os.path.join(os.path.dirname(__file__), self.prompts_file)

    def _ensure_file(self):
        '''Создает файл с промптами если его нет'''
        file_path = self._get_file_path()
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump({}, file, ensure_ascii=False, indent=2)

    def _load_prompts(self):
        '''Загружает все промпты из файла'''
        self._ensure_file()
        file_path = self._get_file_path()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.prompts = json.load(file)
        except:
            self.prompts = {}

    def _save_prompts(self):
        '''Сохраняет все промпты в файл'''
        file_path = self._get_file_path()
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.prompts, file, ensure_ascii=False, indent=2)
        except:
            pass

    def save_prompts(self, chat_id: str, prompt: str):
        '''Сохраняет системный промпт для чата'''
        if not chat_id:
            return False
        if not prompt or not prompt.strip():
            if chat_id in self.prompts:
                del self.prompts[chat_id]
            self._save_prompts()
            return True
        self.prompts[chat_id] = {
            'prompt': prompt.strip(),
            'updated': datetime.now().isoformat()
        }
        self._save_prompts()
        return True

    def get_prompt(self, chat_id: str) -> str:
        '''Получает промпт для чата'''
        if not chat_id:
            return None
        if chat_id in self.prompts:
            return self.prompts[chat_id].get('prompt', '')
        return None

    def delete_prompt(self, chat_id: str):
        '''Удаляет промпт для чата'''
        if chat_id in self.prompts:
            del self.prompts[chat_id]
            self._save_prompts()
            return True
        return False

    def has_prompt(self, chat_id: str) -> bool:
        '''Проверяет наличие промпта для чата'''
        return chat_id in self.prompts
