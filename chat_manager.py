# Импорт зависимостей
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

from kivy.utils import platform

if platform == 'android':
    try:
        from android.storage import app_storage_path
    except:
        app_storage_path = None


# Класс управления чатами
class ChatManager:
    def __init__(self, chat_dir='chats'):
        self.chats_dir = chat_dir
        self.current_chat_id = None
        self.chats_list = []
        self._ensure_chats_dir()
        self._load_chats_list()

        if self.chats_list:
            self.current_chat_id = self.chats_list[0]['id']
        else:
            self._create_new_chat()

    def _get_chats_path(self):
        '''Получает путь к папке с чатами'''
        if platform == 'android':
            return os.path.join(app_storage_path(), self.chats_dir)
        else:
            return os.path.join(os.path.dirname(__file__), self.chats_dir)

    def _ensure_chats_dir(self):
        '''Создает папку для чатов если ее нет'''
        path = self._get_chats_path()
        if not os.path.exists(path):
            os.makedirs(path)

    def get_chat_file_path(self, chat_id: str) -> str:
        '''Получает путь к файлу чата'''
        return os.path.join(self._get_chats_path(), f'{chat_id}.json')

    def _load_chats_list(self):
        '''Загружает список всех чатов'''
        path = self._get_chats_path()
        self.chats_list = []

        if os.path.exists(path):
            for filename in os.listdir(path):
                if filename.endswith('.json'):
                    chat_id = filename[:-5]
                    file_path = os.path.join(path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            name = data.get('name', f'Chats {chat_id}')
                            created = data.get('created', datetime.now().isoformat())
                            self.chats_list.append({
                                'id': chat_id,
                                'name': name,
                                'created': created,
                                'file_path': file_path,
                                'has_messages': bool(data.get('messages'))
                            })
                    except:
                        pass

        self.chats_list.sort(key=lambda el: el['created'], reverse=True)

    def _create_new_chat(self, name: str = None) -> str:
        '''Создает новый чат'''
        chat_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        if name is None:
            name = f'Chat {len(self.chats_list) + 1}'

        chat_data = {
            'name': name,
            'created': datetime.now().isoformat(),
            'messages': []
        }
        file_path = self.get_chat_file_path(chat_id)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(chat_data, file, ensure_ascii=False, indent=2)

        self.chats_list.insert(0, {
            'id': chat_id,
            'name': name,
            'created': chat_data['created'],
            'file_path': file_path,
            'has_messages': False
        })

        self.current_chat_id = chat_id
        return chat_id

    def get_current_chat_messages(self) -> List[Dict]:
        '''Получает сообщения текущего чата'''
        if self.current_chat_id:
            file_path = self.get_chat_file_path(self.current_chat_id)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        return data.get('messages', [])
                except:
                    return []
        return []

    def add_message_to_current_chat(self, role: str, content: str, msg_type: str = 'text'):
        '''Добавляет сообщение в текущий чат'''
        if not self.current_chat_id:
            self._create_new_chat()

        file_path = self.get_chat_file_path(self.current_chat_id)

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    messages = data.get('messages', [])
            except:
                messages = []
        else:
            messages = []

        messages.append({
            'role': role,
            'content': content,
            'msg_type': msg_type,
            'timestamp': datetime.now().isoformat()
        })
        chat_data = {
            'name': self.get_current_chat_name(),
            'created': datetime.now().isoformat(),
            'messages': messages
        }
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(chat_data, file, ensure_ascii=False, indent=2)

        for chat in self.chats_list:
            if chat['id'] == self.current_chat_id:
                chat['has_messages'] = True
                break

        return messages[-1]

    def get_current_chat_name(self) -> str:
        '''Получает имя текущего чата'''
        if self.current_chat_id:
            for chat in self.chats_list:
                if chat['id'] == self.current_chat_id:
                    return chat['name']
        return 'Новый чат'

    def switch_chat(self, chat_id: str):
        '''Переключается на другой чат'''
        exists = any(chat['id'] == chat_id for chat in self.chats_list)
        if exists:
            self.current_chat_id = chat_id
        else:
            self._create_new_chat()

    def create_new_chat(self):
        '''Создает новый чат и переключается на него'''
        return self._create_new_chat()

    def clear_current_chat(self):
        '''Очищает текущий чат'''
        if self.current_chat_id:
            messages = self.get_current_chat_messages()

            from image_generator import delete_images
            for msg in messages:
                if msg.get('msg_type') == 'image':
                    image_path = msg.get('content')
                    if image_path:
                        delete_images(image_path)

            file_path = self.get_chat_file_path(self.current_chat_id)
            if os.path.exists(file_path):
                os.remove(file_path)
            self.chats_list = [chat for chat in self.chats_list if chat['id'] != self.current_chat_id]
            self._create_new_chat()

    def rename_chat(self, chat_id: str, new_name: str):
        '''Переименовывает чат'''
        file_path = self.get_chat_file_path(chat_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                data['name'] = new_name
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)

                for chat in self.chats_list:
                    if chat['id'] == chat_id:
                        chat['name'] = new_name
                        break
            except:
                pass

    def delete_chat(self, chat_id: str):
        '''Удаляет чат'''
        file_path = self.get_chat_file_path(chat_id)
        if os.path.exists(file_path):
            os.remove(file_path)

        self.chats_list = [chat for chat in self.chats_list if chat['id'] != chat_id]

        if self.current_chat_id == chat_id:
            if self.chats_list:
                self.current_chat_id = self.chats_list[0]['id']
            else:
                self._create_new_chat()
