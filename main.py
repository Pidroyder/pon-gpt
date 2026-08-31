# Импорт зависимостей
import threading
import os
import re
import uuid
import shutil

import sys
import traceback
import faulthandler

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import platform

if platform == 'android':
    try:
        from android.storage import app_storage_path
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.INTERNET,
            Permission.RECORD_AUDIO,
            Permission.CAMERA
        ])
    except:
        app_storage_path = None
else:
    app_storage_path = None


# Диагностика крашей лог файла и faulthandler
try:
    if platform == 'android' and app_storage_path:
        _CRASH_LOG = os.path.join(app_storage_path(), 'crash.log')
    else:
        _CRASH_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crash.log')
    _crash_file = open(_CRASH_LOG, 'w', buffering=1, encoding='utf-8')
    def _log(msg):
        try:
            _crash_file.write(msg + '\n')
        except:
            pass
    _log('--- PonGPT boot ---')
    faulthandler.enable(_crash_file)
    def _excepthook(t, v, tb):
        _log(''.join(traceback.format_exception(t, v, tb)))
        sys.__excepthook__(t, v, tb)
    sys.excepthook = _excepthook
except:
    _log = lambda msg: None

from history_manager import HistoryManager
from language_manager import LanguageManager
from prompt_manager import PromptManager
from custom_widgets import Message, ImageMessage, CodeArea
from image_generator import create_image
from voice_input import VoiceInput
from OCR import get_text_from_image
from utils import (on_container_height_change, on_scroll_change,
                   toggle_scroll_button, is_scroll_at_bottom,
                   check_scroll_position, scroll_to_bottom,
                   scroll_to_bottom_if_needed, handle_scroll_change,
                   load_chat_history, scroll_code_areas_to_top,
                   update_all_composite_messages, show_chats_dialog,
                   show_language_dialog, refresh_chats_dialog,
                   show_rename_dialog, select_image, on_image_selected,
                   process_image, on_image_processed, on_image_processed_error,
                   show_prompts_dialog, save_system_prompt, delete_system_prompt,
                   restore_hint_text, update_interface_language)
import model

# Установка режима работы экранной клавиатуры
Window.softinput_mode = 'below_target'


# Создание класса GUI
class GUI(MDBoxLayout):
    '''Главный класс интерфейса чат-приложения'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ids.send_button.bind(on_press=self.send_prompt)
        self.ids.clear_history_button.bind(on_press=self.show_confirm_dialog)
        self.ids.chats_button.bind(on_press=self.show_chats_dialog)
        self.ids.messages_container.bind(height=self._on_container_height_change)
        self.ids.scroll_down_button.bind(on_release=self.scroll_to_bottom)
        self.ids.language_changer.bind(on_press=self.show_language_dialog)
        self.ids.voice_button.bind(on_release=self.toggle_voice_recording)
        self.ids.prompt_setter_button.bind(on_press=self.show_prompts_dialog)
        self.ids.send_image_button.bind(on_press=self.select_image)

        self.history_manager = HistoryManager()
        self.language_manager = LanguageManager()
        self.prompt_manager = PromptManager()

        try:
            with open(self.language_manager.get_file_path(), 'r', encoding='utf-8') as file:
                self.language = file.read().strip()
        except:
            self.language = 'RU'

        self.language = self.language_manager.get_saved_language()
        self.texts = self.language_manager.translate_interface(self.language)

        self.ids.prompt_input.hint_text = self.texts['prompt_input']

        # Устанавливаем флаги
        self.voice_input = None
        self._is_recording = False
        self._is_processing = False
        self.dialog = None
        self._is_user_scrolled_up = False
        self.loading_message = None
        self._is_scrolling_to_bottom = False
        if not self.history_manager.get_history():
            self.ids.clear_history_button.disabled = True

        self._load_chat_history()
        self.print_chat_name()

        Clock.schedule_once(lambda dt: self._update_all_composite_messages(), .3)
        Clock.schedule_once(lambda dt: self._update_all_composite_messages(), .6)

    def _load_chat_history(self):
        '''Загружает историю чата при запуске'''
        load_chat_history(self)

    def _scroll_code_areas_to_top(self, container):
        '''Прокручивает все CodeArea в контейнере вверх'''
        scroll_code_areas_to_top(self, container)

    def _update_all_composite_messages(self):
        '''Обновляет все составные сообщения в чате'''
        update_all_composite_messages(self)

    def on_scroll_change(self, scroll_y):
        '''Обрабатывает изменение позиции прокрутки'''
        handle_scroll_change(scroll_y, self)

    def _on_container_height_change(self, instance, value):
        '''Вызывается при изменении размера контейнера'''
        on_container_height_change(
            self.ids.messages_container,
            self._is_scrolling_to_bottom,
            self._check_scroll_position
        )

    def _check_scroll_position(self):
        '''Проверяет позицию прокрутки и обновляет кнопку'''
        is_user_scrolled_up = check_scroll_position(
            self.ids.messages_scroll,
            self.ids.scroll_down_button,
            self.ids.messages_container
        )
        if is_user_scrolled_up is not None:
            self._is_user_scrolled_up = is_user_scrolled_up

    def _release_scroll_lock(self):
        '''Снимает блокировку и проверяет позицию'''
        self._is_scrolling_to_bottom = False

    def scroll_to_bottom(self, instance=None):
        '''Покручивает чат в самый низ'''
        scroll_to_bottom(
            self.ids.messages_scroll,
            self.ids.messages_container,
            self.ids.scroll_down_button,
            self._release_scroll_lock
        )
        self._is_scrolling_to_bottom = True
        self._is_user_scrolled_up = False

    def _scroll_to_bottom_if_needed(self):
        '''Прокручивает вниз если пользователь не прокрутил вверх'''
        scroll_to_bottom_if_needed(
            self._is_user_scrolled_up,
            self.scroll_to_bottom
        )

    def send_prompt(self, instance):
        '''Метод отправки промпта'''
        if self._is_processing:
            return

        prompt = self.ids.prompt_input.text
        if not prompt.strip():
            return

        self.ids.prompt_input.text = ''

        self._is_processing = True
        self.ids.send_button.disabled = True
        self.ids.clear_history_button.disabled = False

        self.history_manager.add_message('user', prompt, 'text')

        # Отображение сообщения пользователя
        message = self._create_message(text=prompt, align='right', role='user')
        container = self.ids.messages_container
        container.add_widget(message)

        # Отображение сообщения загрузки
        self.loading_message = Message(text=self.texts['loading_message'], align='left', role='assistant')
        container.add_widget(self.loading_message)

        Clock.schedule_once(lambda dt: self.update_container(), 0)
        Clock.schedule_once(lambda dt: self.update_container(), .1)
        Clock.schedule_once(lambda dt: self.update_container(), .3)

        Clock.schedule_once(lambda dt: self._scroll_to_bottom_if_needed(), .2)

        is_draw = self._is_draw_command(prompt)

        if is_draw:
            threading.Thread(target=self._process_image_generation, args=(prompt,)).start()
        else:
            threading.Thread(target=self._process_response, args=(prompt,)).start()

    def _process_response(self, prompt):
        '''
        Передает промпт в функцию получения
        ответа от нейросети
        '''
        response = model.get_ai_response(prompt, self.language)
        Clock.schedule_once(lambda dt: self.send_ai_response(response), 0)

    def send_ai_response(self, response):
        '''Отправляет ответ от нейросети'''
        container = self.ids.messages_container
        try:
            if self.loading_message and self.loading_message in container.children:
                container.remove_widget(self.loading_message)
            if response:
                self.history_manager.add_message('assistant', response, 'text')
                message = self._create_message(text=response, align='left', role='assistant')
            else:
                error_message = self.texts['response_error']
                self.history_manager.add_message('assistant', error_message, 'text')
                message = self._create_message(text=error_message, align='left', role='assistant')
            container.add_widget(message)
        except:
            error_message = self.texts['request_error']
            self.history_manager.add_message('assistant', error_message, 'text')
            message = self._create_message(text=error_message, align='left', role='assistant')
            container.add_widget(message)
        finally:
            self._is_processing = False
            self.ids.send_button.disabled = False

            Clock.schedule_once(lambda dt: self.update_container(), 0)
            Clock.schedule_once(lambda dt: self.update_container(), .1)

            Clock.schedule_once(lambda dt: self._scroll_to_bottom_if_needed(), .2)
            Clock.schedule_once(lambda dt: self._scroll_to_bottom_if_needed(), .4)
            Clock.schedule_once(lambda dt: self._scroll_to_bottom_if_needed(), .6)

    def update_container(self):
        '''Обновляет контейнер'''
        container = self.ids.messages_container
        container.height = container.minimum_height

    def _create_message(self, text, align, role):
        '''Создает сообщение с поддержкой кода'''
        code_pattern = r'\[code\](.*?)\[/code\]'

        if re.search(code_pattern, text, re.DOTALL):
            parts = re.split(code_pattern, text, flags=re.DOTALL)

            container = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=dp(10),
                padding=[0, dp(5), 0, dp(5)]
            )
            container.height = 0
            container.width = Window.width * .8
            container.size_hint_x = None

            for i, part in enumerate(parts):
                if not part.strip():
                    continue
                if i % 2 == 0:
                    msg = Message(text=part.strip(), align=align, role=role)
                    msg.width = container.width
                    container.add_widget(msg)
                else:
                    code_area = CodeArea(code=part.strip(), align=align, role=role)
                    code_area.width = container.width
                    container.add_widget(code_area)
                    Clock.schedule_once(lambda dt, ca=code_area: ca._update_size(), .2)

            Clock.schedule_once(lambda dt: self._update_container_children(container), .05)
            Clock.schedule_once(lambda dt: self._update_container_children(container), .15)
            Clock.schedule_once(lambda dt: self._update_container_children(container), .3)
            return container
        else:
            return Message(text=text, align=align, role=role)

    def _update_container_height(self, container):
        '''Обновляет высоту контейнера'''
        container.height = container.minimum_height

    def _update_container_children(self, container):
        '''Обновляет все дочерние элементы контейнера'''
        if not container or not container.children:
            return

        for child in container.children:
            if hasattr(child, 'set_width'):
                child.set_width(container.width)
            elif hasattr(child, 'width'):
                child.width = container.width
                if isinstance(child, Message):
                    child._update_size()
                elif isinstance(child, CodeArea):
                    child._build_code()

        container.height = container.minimum_height
        container.size_hint_y = None

        self.update_container()
        Clock.schedule_once(lambda dt: self._force_container_update(container), .1)

    def _force_container_update(self, container):
        '''Принудительное обновление контейнера'''
        container.height = container.minimum_height
        self.update_container()

    def show_chats_dialog(self, instance=None):
        '''Показывает диалог со списком чатов'''
        show_chats_dialog(self, instance)

    def show_language_dialog(self, instance):
        '''Показывает диалог с языками'''
        show_language_dialog(self, instance)

    def _refresh_chats_dialog(self):
        '''Обновляет содержимое диалога чатов'''
        refresh_chats_dialog(self)

    def show_rename_dialog(self, chat_id, current_name):
        '''Показывает диалог переименовывания чата'''
        show_rename_dialog(self, chat_id, current_name)

    def show_confirm_dialog(self, instance):
        '''Показывает диалог подтверждения очистки чата'''
        if self.dialog:
            return

        if not self.history_manager.get_history():
            return

        self.ids.clear_history_button.disabled = True

        self.dialog = MDDialog(
            title=self.texts['dialog_title'],
            text=self.texts['dialog_text'],
            buttons=[
                MDRaisedButton(
                    text=self.texts['confirm_clear_button'],
                    text_color=(0, 1, 0, 1),
                    md_bg_color=(0, 1, 0, .5),
                    on_press=self.confirm_clear
                ),
                MDRaisedButton(
                    text=self.texts['cancel_clear_button'],
                    text_color=(1, 0, 0, 1),
                    md_bg_color=(1, 0, 0, .5),
                    on_press=self.cancel_clear
                )
            ]
        )
        self.dialog.bind(on_dismiss=self._on_dialog_dismiss)
        self.dialog.open()

    def _on_dialog_dismiss(self, instance):
        '''Обрабатывает закрытие диалога (по клику вне его)'''
        if self.history_manager.get_history():
            self.ids.clear_history_button.disabled = False
        self.dialog = None

    def confirm_clear(self, instance):
        '''Подтверждает очистку чата'''
        self.history_manager.clear_history()
        container = self.ids.messages_container
        container.clear_widgets()
        Clock.schedule_once(lambda dt: self.update_container(), -1)
        self.dialog.dismiss()
        self.dialog = None
        self.ids.clear_history_button.disabled = True
        self.loading_message = None

    def cancel_clear(self, instance):
        '''Отменяет очистку чата'''
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            if self.history_manager.get_history():
                self.ids.clear_history_button.disabled = False

    def create_new_chat(self, instance):
        '''Создает новый чат'''
        self.history_manager.chat_manager.create_new_chat()
        self.ids.messages_container.clear_widgets()
        self._load_chat_history()
        self._update_clear_button_state()
        self.print_chat_name()

        Clock.schedule_once(lambda dt: self._update_all_composite_messages(), .2)

        if hasattr(self, 'chats_dialog') and self.chats_dialog:
            self.chats_dialog.dismiss()
        self.show_chats_dialog()

    def _update_clear_button_state(self):
        '''Обновляет состояние кнопки очистки в зависимости от наличия сообщений'''
        if self.history_manager.get_history():
            self.ids.clear_history_button.disabled = False
        else:
            self.ids.clear_history_button.disabled = True

    def switch_chat(self, chat_id):
        '''Переключается на другой чат'''
        self.history_manager.switch_chat(chat_id)
        self.ids.messages_container.clear_widgets()
        self._load_chat_history()
        self._update_clear_button_state()
        self.print_chat_name()

        Clock.schedule_once(lambda dt: self._update_all_composite_messages(), .2)
        Clock.schedule_once(lambda dt: self._update_all_composite_messages(), .5)

        if hasattr(self, 'chats_dialog') and self.chats_dialog:
            self.chats_dialog.dismiss()

    def rename_chat(self, chat_id, new_name, dialog):
        '''Переименовывает чат'''
        if self.chats_dialog:
            self.chats_dialog.dismiss()
        if new_name and new_name.strip():
            self.history_manager.chat_manager.rename_chat(chat_id, new_name.strip())
            dialog.dismiss()

            if hasattr(self, 'chat_dialog') and self.chats_dialog:
                self.chats_dialog.dismiss()
            self.show_chats_dialog()

    def print_chat_name(self):
        '''Отображает имя чата на верхней панели'''
        chat_name = self.history_manager.chat_manager.get_current_chat_name()
        chat_id = self.history_manager.chat_manager.current_chat_id

        has_prompt = self.prompt_manager.has_prompt(chat_id)
        prompt_indicator = ' [P]' if has_prompt else ''

        if len(chat_name) > 20:
            self.ids.chat_name_label.text = f'[b]{chat_name[:20]}...{prompt_indicator}[/b]'
        else:
            self.ids.chat_name_label.text = f'[b]{chat_name}{prompt_indicator}[/b]'

    def change_language(self, lang: str):
        '''Меняет язык системы'''
        self.language = lang
        self.language_manager.add_language_to_file(self.language)
        self.texts = self.language_manager.translate_interface(self.language)
        self._update_interface_language()
        if hasattr(self, 'language_dialog') and self.language_dialog:
            self.language_dialog.dismiss()
            self.language_dialog = None

    def _update_interface_language(self):
        '''Обновляет все тексты интерфейса в соответствии с текущим языком'''
        update_interface_language(self)

    def select_image(self, instance):
        '''Открывает диалог выбора изображения'''
        select_image(self, instance)

    def _on_image_selected(self, filechooser):
        '''Обрабатывает выбор изображения'''
        on_image_selected(self, filechooser)

    def _process_image(self, image_path):
        '''Обрабатывает изображение в отдельном потоке'''
        process_image(self, image_path)

    def open_link(self):
        '''Открывает ссылку в системном браузере через Android Intent'''
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_VIEW,
                            Uri.parse('https://github.com/Pidroyder/pon-gpt'))
            activity.startActivity(intent)
        except Exception:
            pass

    def _on_image_processed(self, text, image_path):
        '''Обрабатывает успешное распознавание текста'''
        on_image_processed(self, text, image_path)

    def _on_image_processed_error(self, error_message):
        '''Обрабатывает ошибку распознавания'''
        on_image_processed_error(self, error_message)

    def _get_sent_images_dir_path(self, dir_name='sent_images') -> str:
        '''Получает путь к папке с отправленными изображениями'''
        if platform == 'android':
            return os.path.join(app_storage_path(), dir_name)
        else:
            return os.path.join(os.path.dirname(__file__), dir_name)

    def send_image_response(self, image_path: str, prompt: str):
        '''Отправляет изображение в чат'''
        container = self.ids.messages_container
        try:
            if self.loading_message and self.loading_message in container.children:
                container.remove_widget(self.loading_message)

            filename = os.path.basename(image_path)
            self.history_manager.add_message('assistant', filename, 'image')

            images_dir = self._get_images_dir_path()
            full_path = os.path.join(images_dir, filename)

            image_message = ImageMessage(image_path=full_path, align='left', role='assistant')
            container.add_widget(image_message)

            Clock.schedule_once(lambda dt: self.update_container(), -1)
        except:
            error_message = self.texts.get('image_error', 'Ошибка отображения изображения')
            self.send_ai_response(error_message)
        finally:
            self._is_processing = False
            self.ids.send_button.disabled = False

    def _get_images_dir_path(self, dir_name='images') -> str:
        '''Получает путь к папке с изображениями'''
        if platform == 'android':
            return os.path.join(app_storage_path(), dir_name)
        else:
            return os.path.join(os.path.dirname(__file__), dir_name)

    def _process_image_generation(self, prompt: str):
        '''Обрабатывает генерацию изображения'''
        try:
            filename = f'image_{uuid.uuid4().hex[:8]}'
            image_path = create_image(prompt, filename)

            if image_path:
                Clock.schedule_once(lambda dt: self.send_image_response(image_path, prompt), 0)
            else:
                error_message = self.texts.get('image_error', 'Ошибка генерации изображения')
                Clock.schedule_once(lambda dt: self.send_ai_response(error_message), 0)
        except:
            error_message = self.texts.get('image_error', 'Ошибка генерации изображения')
            Clock.schedule_once(lambda dt: self.send_ai_response(error_message), 0)

    def show_prompts_dialog(self, instance):
        '''Показывает диалог добавления промпта'''
        show_prompts_dialog(self, instance)

    def save_system_prompt(self, instance):
        '''Сохраняет системный промпт'''
        save_system_prompt(self, instance)

    def delete_system_prompt(self, instance):
        '''Удаляет системный промпт'''
        delete_system_prompt(self, instance)

    def _restore_hint_text(self):
        '''Восстанавливает стандартную подсказку'''
        restore_hint_text(self)

    def on_prompt_text_change(self, text):
        '''Обрабатывает изменение текста в поле ввода'''
        voice_button = self.ids.voice_button
        if text and text.strip():
            voice_button.disabled = True
            voice_button.icon = 'microphone'
            voice_button.md_bg_color = (0, 0, 1, .3)
        else:
            voice_button.disabled = False

    def toggle_voice_recording(self, instance):
        '''Переключает состояние записи голоса'''
        if self._is_recording:
            self.stop_voice_recording()
        else:
            self.start_voice_recording()

    def start_voice_recording(self):
        '''Начинает запись голоса'''
        if self._is_processing:
            return
        if self.ids.prompt_input.text.strip():
            return
        if not self.voice_input:
            try:
                self.voice_input = VoiceInput()
            except Exception as e:
                _log(f'VoiceInput init error: {e}')
                self.ids.prompt_input.hint_text = self.texts['voice_error']
                Clock.schedule_once(lambda dt: self._restore_hint_text(), 3)
                return

        voice_button = self.ids.voice_button
        voice_button.icon = 'circle'
        voice_button.md_bg_color = (1, 0, 0, .5)
        voice_button.icon_color = (1, 1, 1, 1)
        self._is_recording = True
        self.voice_input.start_recording(self.on_voice_input_result)

    def stop_voice_recording(self):
        '''Останавливает запись голоса'''
        self._is_recording = False
        if self.voice_input:
            self.voice_input.stop_recording()

        voice_button = self.ids.voice_button
        voice_button.icon = 'microphone'
        voice_button.md_bg_color = (0, 0, 1, .5)
        voice_button.icon_color = (0, 0, 1, 1)

    def on_voice_input_result(self, text, error=None):
        '''Обрабатывает результат распознавания'''
        self._is_recording = False
        voice_button = self.ids.voice_button
        voice_button.icon = 'microphone'
        voice_button.md_bg_color = (0, 0, 1, .5)
        voice_button.icon_color = (0, 0, 1, 1)
        if error:
            _log(f'Voice error: {error}')
            self.ids.prompt_input.hint_text = f'{self.texts["voice_error"]}: {error}'
            Clock.schedule_once(lambda dt: self._restore_hint_text(), 4)
            return

        if text:
            self.ids.prompt_input.text = text
            Clock.schedule_once(lambda dt: self.send_prompt(None), .1)

    def _clear_error_text(self):
        '''Очищает текст ошибки'''
        if self.ids.prompt_input.text.startswith('Error:') or self.ids.prompt_input.text.startswith('Ошибка:'):
            self.ids.prompt_input.text = ''

    def get_confirm_texts(self):
        '''Получает слова подтверждения для кнопок'''
        confirm_texts = []
        languages = self.language_manager.get_available_languages()
        translations = self.language_manager.load_translations()
        for language in languages:
            confirm_texts.append(translations[language])
        return confirm_texts

    def get_cancel_texts(self):
        '''Получает слова отмены для кнопок'''
        cancel_texts = []
        languages = self.language_manager.get_available_languages()
        translations = self.language_manager.load_translations()
        for language in languages:
            cancel_texts.append(translations[language])
        return cancel_texts

    def get_close_texts(self):
        '''Получает слова закрытия для кнопок'''
        close_texts = []
        languages = self.language_manager.get_available_languages()
        translations = self.language_manager.load_translations()
        for language in languages:
            close_texts.append(translations[language])
        return close_texts

    def _is_draw_command(self, prompt: str) -> bool:
        '''Проверяет, является ли запрос командой на рисование'''
        draw_keywords = ['нарисуй', 'нарисуйте', 'создай', 'сделай']
        prompt_lower = prompt.lower().strip()

        for keyword in draw_keywords:
            if prompt_lower.startswith(keyword):
                return True
        return False


# Заполнение интерфейса
class PonGPTApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        return GUI()


# Запуск программы
if __name__ == '__main__':
    try:
        PonGPTApp().run()
    except Exception:
        _tb = traceback.format_exc()
        _log(_tb)
        try:
            from kivy.app import App
            from kivy.uix.label import Label
            from kivy.uix.scrollview import ScrollView
            from kivy.uix.boxlayout import BoxLayout
            from kivy.core.window import Window
            Window.clearcolor = (.08, 0, 0, 1)

            class CrashApp(App):
                def build(self):
                    root = BoxLayout()
                    sv = ScrollView()
                    lbl = Label(text=_tb, color=(1, .35, .35, 1),
                                font_size='11sp', halign='left', valign='top')
                    lbl.bind(width=lambda i, w: setattr(lbl, 'text_size', (w, None)))
                    sv.add_widget(lbl)
                    root.add_widget(sv)
                    return root
            CrashApp().run()
        except Exception:
            pass
