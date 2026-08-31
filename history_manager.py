# Импорт зависимостей
from chat_manager import ChatManager


# Класс управления историей
class HistoryManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HistoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.chat_manager = ChatManager()

    def get_file_path(self):
        '''Получает путь к файлу истории'''
        return self.chat_manager.get_chat_file_path(self.chat_manager.current_chat_id)

    def add_message(self, role: str, content: str, msg_type: str = 'text'):
        '''Добавляет сообщение в историю'''
        return self.chat_manager.add_message_to_current_chat(role, content, msg_type)

    def get_history(self) -> list:
        '''Возвращает всю историю'''
        return self.chat_manager.get_current_chat_messages()

    def get_last_n_messages(self, n: int) -> list:
        '''Возвращает последние n сообщений'''
        messages = self.get_history()
        return messages[-n:] if messages else []

    def clear_history(self):
        '''Очищает историю'''
        self.chat_manager.clear_current_chat()

    def switch_chat(self, chat_id: str):
        '''Переключает на другой чат'''
        self.chat_manager.switch_chat(chat_id)

    def save_history(self):
        '''Сохраняет историю'''
        self.chat_manager.save_current_chat()
