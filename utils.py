# Импорт зависимостей
import os
import shutil
import threading
import uuid

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconRightWidget
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform as _platform

from custom_widgets import CodeArea, ImageMessage


def _is_android():
    '''Определяет, запущено ли приложение на Android, без зависимости от глобального `platform`'''
    try:
        return _platform == 'android'
    except Exception:
        try:
            import jnius_config
            return True
        except Exception:
            return False
from OCR import get_text_from_image


# Функции для работы с историей
def load_chat_history(self):
    '''Загружает историю чата при запуске'''
    history = self.history_manager.get_history()
    if history:
        container = self.ids.messages_container
        images_dir = self._get_images_dir_path()
        for msg in history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            msg_type = msg.get('msg_type', 'text')
            align = 'right' if role == 'user' else 'left'

            if msg_type == 'image':
                try:
                    full_path = os.path.join(images_dir, content)
                    if os.path.exists(full_path):
                        image_message = ImageMessage(image_path=full_path, align=align, role=role)
                        container.add_widget(image_message)
                        Clock.schedule_once(lambda dt, img=image_message: img._update_size(), .1)
                        Clock.schedule_once(lambda dt, img=image_message: img._update_size(), .3)
                    else:
                        message = self._create_message(text='[Изображение] (файл не найден)', align=align, role=role)
                        container.add_widget(message)
                except:
                    message = self._create_message(text='[Изображение] (файл не найден)', align=align, role=role)
                    container.add_widget(message)
            else:
                message = self._create_message(text=content, align=align, role=role)
                container.add_widget(message)
                if isinstance(message, MDBoxLayout) and len(message.children) > 0:
                    Clock.schedule_once(lambda dt, msg=message: self._update_container_children(msg), .1)
                    Clock.schedule_once(lambda dt, msg=message: self._update_container_children(msg), .3)
                    Clock.schedule_once(lambda dt, msg=message: self._update_container_children(msg), .5)
                    Clock.schedule_once(lambda dt, msg=message: self._scroll_code_areas_to_top(msg), .6)

        Clock.schedule_once(lambda dt: self.update_container(), -1)
        Clock.schedule_once(lambda dt: self.update_container(), .1)


def scroll_code_areas_to_top(self, container):
    '''Прокручивает все CodeArea в контейнере вверх'''
    if isinstance(container, MDBoxLayout):
        for child in container.children:
            if isinstance(child, CodeArea):
                child._scroll_to_top()


def update_all_composite_messages(self):
    '''Обновляет все составные сообщения в чате'''
    container = self.ids.messages_container
    for child in container.children:
        if isinstance(child, MDBoxLayout):
            if len(child.children) > 1 or any(isinstance(chat, CodeArea) for chat in child.children):
                Clock.schedule_once(lambda dt, msg=child: self._update_container_children(msg), .1)
                Clock.schedule_once(lambda dt, msg=child: self._update_container_children(msg), .3)
                Clock.schedule_once(lambda dt, msg=child: self._update_container_children(msg), .5)


# Функции для работы с прокруткой
def on_container_height_change(container, is_scrolling_to_bottom, check_scroll_callback):
    '''Вызывается при изменении размера контейнера'''
    if not is_scrolling_to_bottom:
        Clock.schedule_once(lambda dt: check_scroll_callback(), 0.1)


def on_scroll_change(scroll_y, is_scrolling_to_bottom, scroll_down_button, messages_scroll, messages_container):
    '''Обрабатывает изменение позиции прокрутки'''
    if is_scrolling_to_bottom:
        return

    is_at_bottom = is_scroll_at_bottom(messages_scroll, messages_container)
    toggle_scroll_button(not is_at_bottom, scroll_down_button)

    return not is_at_bottom


def toggle_scroll_button(show, scroll_down_button):
    '''Показывает или скрывает кнопку прокрутки'''
    if show:
        scroll_down_button.opacity = 1
        scroll_down_button.disabled = False
    else:
        scroll_down_button.opacity = 0
        scroll_down_button.disabled = True


def is_scroll_at_bottom(messages_scroll, messages_container, threshold=.01):
    '''Проверяет находится ли прокрутка внизу'''
    if messages_container.height <= messages_scroll.height:
        return True
    return messages_scroll.scroll_y <= threshold


def check_scroll_position(messages_scroll, scroll_down_button, messages_container):
    '''Проверяет позицию прокрутки и обновляет кнопку'''
    if hasattr(messages_scroll, '_update_scroll_y'):
        messages_scroll._update_scroll_y()
    return on_scroll_change(
        messages_scroll.scroll_y,
        False,
        scroll_down_button,
        messages_scroll,
        messages_container
    )


def scroll_to_bottom(messages_scroll, messages_container, scroll_down_button, release_lock_callback):
    '''Покручивает чат в самый низ'''
    if messages_container.children:
        toggle_scroll_button(False, scroll_down_button)
        last_child = messages_container.children[0]
        messages_scroll.scroll_to(last_child)
        Clock.schedule_once(lambda dt: release_lock_callback(), .5)
        return True
    return False


def scroll_to_bottom_if_needed(is_user_scrolled_up, scroll_to_bottom_callback):
    '''Прокручивает вниз если пользователь не прокрутил вверх'''
    if not is_user_scrolled_up:
        scroll_to_bottom_callback(None)


def handle_scroll_change(scroll_y, self):
    '''Обрабатывает изменение прокрутки из kv'''
    if hasattr(self, '_is_scrolling_to_bottom') and self._is_scrolling_to_bottom:
        return

    is_at_bottom = is_scroll_at_bottom(
        self.ids.messages_scroll,
        self.ids.messages_container
    )
    toggle_scroll_button(not is_at_bottom, self.ids.scroll_down_button)

    if not is_at_bottom:
        self._is_user_scrolled_up = True
    else:
        self._is_user_scrolled_up = False


# Функции для работы с диалогами
def show_chats_dialog(self, instance=None):
    '''Показывает диалог со списком чатов'''
    if not hasattr(self, 'texts'):
        self.texts = self.language_manager.translate_interface()[self.language]

    chats = self.history_manager.chat_manager.chats_list
    list_view = MDList()
    new_chat_item = OneLineAvatarIconListItem(
        text=self.texts['new_chat_item'],
        on_press=self.create_new_chat,
        bg_color=(0, 0, 1, .3)
    )
    new_chat_item.add_widget(IconRightWidget(icon='plus'))
    list_view.add_widget(new_chat_item)

    if chats:
        for chat in chats:
            chat_item = OneLineAvatarIconListItem(
                text=chat['name'],
                on_press=lambda instance, chat_id=chat['id']: self.switch_chat(chat_id),
                bg_color=(.2, .2, .2, 1) if chat['id'] != self.history_manager.chat_manager.current_chat_id else (
                    0, 0, 1, .5)
            )

            rename_icon = IconRightWidget(
                icon='pencil',
                on_press=lambda instance, chat_id=chat['id'], name=chat['name']: self.show_rename_dialog(chat_id,
                                                                                                         name)
            )
            chat_item.add_widget(rename_icon)

            list_view.add_widget(chat_item)
    else:
        no_chats_item = OneLineAvatarIconListItem(
            text=self.texts['no_chats_item'],
            disabled=True
        )
        list_view.add_widget(no_chats_item)

    scroll_view = MDScrollView(
        size_hint_y=None,
        height=dp(400)
    )
    scroll_view.add_widget(list_view)

    self.chats_dialog = MDDialog(
        title=self.texts['chats_dialog_title'],
        type='custom',
        content_cls=scroll_view,
        size_hint=(.9, None),
        height=dp(500),
        buttons=[
            MDRaisedButton(
                text=self.texts['close_button'],
                on_press=lambda instance: self.chats_dialog.dismiss(),
                text_color=(1, 0, 0, 1),
                md_bg_color=(1, 0, 0, .5)
            )
        ]
    )
    self.chats_dialog.open()


def show_language_dialog(self, instance):
    '''Показывает диалог с языками'''
    lang_list = MDList()
    languages = self.language_manager.get_available_languages()
    for code, name in languages.items():
        lang_item = OneLineAvatarIconListItem(
            text=f'{code} {name}',
            on_press=lambda instance, lang_code=code: self.change_language(lang_code)
        )
        if code == self.language:
            lang_item.bg_color = (0, 0, 1, .3)
        lang_list.add_widget(lang_item)
    content_scroll = MDScrollView(
        size_hint_y=None,
        height=dp(400)
    )
    content_scroll.add_widget(lang_list)
    self.language_dialog = MDDialog(
        title=self.texts['language_dialog'],
        type='custom',
        content_cls=content_scroll,
        size_hint=(.9, None),
        height=dp(500),
        buttons=[
            MDRaisedButton(
                text=self.texts['close_button'],
                on_press=lambda instance: self.language_dialog.dismiss(),
                text_color=(1, 0, 0, 1),
                md_bg_color=(1, 0, 0, .5)
            )
        ]
    )
    self.language_dialog.open()


def refresh_chats_dialog(self):
    '''Обновляет содержимое диалога чатов'''
    if hasattr(self, 'chats_dialog') and self.chats_dialog:
        dialog = self.chats_dialog

        chats = self.history_manager.chat_manager.chats_list
        list_view = MDList()
        new_chat_item = OneLineAvatarIconListItem(
            text=self.texts['new_chat_item'],
            on_press=self.create_new_chat,
            bg_color=(0, 0, 1, .3)
        )
        new_chat_item.add_widget(IconRightWidget(icon='plus'))
        list_view.add_widget(new_chat_item)

        if chats:
            for chat in chats:
                chat_item = OneLineAvatarIconListItem(
                    text=chat['name'],
                    on_press=lambda instance, chat_id=chat['id']: self.switch_chat(chat_id),
                    bg_color=(.2, .2, .2, 1) if chat[
                                                    'id'] != self.history_manager.chat_manager.current_chat_id else (
                        0, 0, 1, .5)
                )

                rename_icon = IconRightWidget(
                    icon='pencil',
                    on_press=lambda instance, chat_id=chat['id'], name=chat['name']: self.show_rename_dialog(
                        chat_id,
                        name)
                )
                chat_item.add_widget(rename_icon)

                list_view.add_widget(chat_item)
        else:
            no_chats_item = OneLineAvatarIconListItem(
                text=self.texts['no_chats_item'],
                disabled=True
            )
            list_view.add_widget(no_chats_item)

        scroll_view = MDScrollView(
            size_hint_y=None,
            height=dp(400)
        )
        scroll_view.add_widget(list_view)
        dialog.content_cls = scroll_view


def show_rename_dialog(self, chat_id, current_name):
    '''Показывает диалог переименовывания чата'''
    content = MDBoxLayout(
        orientation='vertical',
        spacing=dp(10),
        size_hint_y=None,
        height=dp(100),
        padding=dp(10)
    )
    text_field = MDTextField(
        text=current_name,
        hint_text=self.texts['text_field'],
        mode='rectangle',
        size_hint_y=None,
        height=dp(50),
        max_text_length=20
    )
    content.add_widget(text_field)

    rename_dialog = MDDialog(
        title=self.texts['rename_dialog_title'],
        type='custom',
        content_cls=content,
        buttons=[
            MDRaisedButton(
                text=self.texts['cancel_rename_button'],
                on_press=lambda instance: rename_dialog.dismiss(),
                text_color=(1, 0, 0, 1),
                md_bg_color=(1, 0, 0, .5)
            ),
            MDRaisedButton(
                text=self.texts['confirm_rename_button'],
                on_press=lambda instance: self.rename_chat(chat_id, text_field.text, rename_dialog),
                text_color=(0, 1, 0, 1),
                md_bg_color=(0, 1, 0, .5)
            )
        ]
    )
    rename_dialog.open()


# Функции для работы с изображениями
def select_image(self, instance):
    '''Открывает диалог выбора изображения'''
    if self._is_processing:
        return

    if _is_android():
        try:
            from android_image_picker import pick_image
            pick_image(lambda path: Clock.schedule_once(
                lambda dt: _on_native_image_picked(self, path), 0))
        except Exception as e:
            if hasattr(self, '_log'):
                try:
                    self._log(f'Image picker error: {e}')
                except Exception:
                    pass
            else:
                print(f'Image picker error: {e}')
        return

    start_path = os.path.expanduser('~')

    filechooser = FileChooserIconView(
        path=start_path,
        filters=['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp'],
        size_hint=(.9, .9),
        dirselect=False
    )

    buttons = [
        MDRaisedButton(
            text='Перейти в /sdcard',
            text_color=(0, 1, 1, 1),
            md_bg_color=(0, .5, .5, .5),
            on_press=lambda instance: setattr(filechooser, 'path', '/sdcard')
        ),
        MDRaisedButton(
            text='Перейти в Download',
            text_color=(0, 1, 1, 1),
            md_bg_color=(0, .5, .5, .5),
            on_press=lambda instance: setattr(filechooser, 'path', '/sdcard/Download')
        ),
        MDRaisedButton(
            text='Перейти в Pictures',
            text_color=(0, 1, 1, 1),
            md_bg_color=(0, .5, .5, .5),
            on_press=lambda instance: setattr(filechooser, 'path', '/sdcard/Pictures')
        ),
        MDRaisedButton(
            text=self.texts['select_button'],
            text_color=(0, 1, 0, 1),
            md_bg_color=(0, 1, 0, .5),
            on_press=lambda instance: self._on_image_selected(filechooser)
        ),
        MDRaisedButton(
            text=self.texts['cancel_button'],
            text_color=(1, 0, 0, 1),
            md_bg_color=(1, 0, 0, .5),
            on_press=lambda instance: popup.dismiss()
        )
    ]

    content = MDBoxLayout(
        orientation='vertical',
        spacing=dp(10),
        padding=dp(10)
    )
    content.add_widget(filechooser)

    nav_container = MDBoxLayout(
        orientation='horizontal',
        size_hint_y=None,
        height=dp(40),
        spacing=dp(5)
    )
    for button in buttons[:3]:
        nav_container.add_widget(button)
    content.add_widget(nav_container)

    button_container = MDBoxLayout(
        orientation='horizontal',
        size_hint_y=None,
        height=dp(50),
        spacing=dp(10)
    )
    for button in buttons[3:]:
        button_container.add_widget(button)
    content.add_widget(button_container)

    popup = Popup(
        title=self.texts['image_select_title'],
        content=content,
        size_hint=(.95, .95),
        auto_dismiss=False
    )
    popup.open()

    self._image_popup = popup


def _on_native_image_picked(self, path):
    if not path:
        try:
            self._log('pick_image: no path returned from picker')
        except Exception:
            pass
        try:
            self.ids.prompt_input.hint_text = 'Не удалось получить изображение'
            Clock.schedule_once(lambda dt: self._restore_hint_text(), 3)
        except Exception:
            pass
        return
    try:
        self._log(f'pick_image: picked path={path}')
    except Exception:
        pass
    _start_image_processing(self, path)


def on_image_selected(self, filechooser):
    '''Обрабатывает выбор изображения'''
    if not filechooser.selection:
        return
    selected_file = filechooser.selection[0]
    if hasattr(self, '_image_popup'):
        self._image_popup.dismiss()
    _start_image_processing(self, selected_file)


def _start_image_processing(self, selected_file):
    threading.Thread(target=self._process_image, args=(selected_file,)).start()

    self.ids.prompt_input.text = self.texts['ocr_processing']
    self.ids.prompt_input.disabled = True
    self.ids.send_button.disabled = True


def process_image(self, image_path):
    '''Обрабатывает изображение в отдельном потоке'''
    try:
        sent_image_dir = self._get_sent_images_dir_path()
        if not os.path.exists(sent_image_dir):
            os.makedirs(sent_image_dir)

        filename = f'user_image_{uuid.uuid4().hex[:8]}{os.path.splitext(image_path)[1]}'
        dest_path = os.path.join(sent_image_dir, filename)

        shutil.copy2(image_path, dest_path)
        text = get_text_from_image(filename)

        if text and text.strip():
            Clock.schedule_once(lambda dt: self._on_image_processed(text, dest_path), 0)
        else:
            Clock.schedule_once(lambda dt: self._on_image_processed_error(self.texts['ocr_no_text']), 0)
    except Exception as e:
        error_msg = str(e)
        Clock.schedule_once(lambda dt: self._on_image_processed_error(f"{self.texts['ocr_error_message']}: {error_msg}"), 0)


def on_image_processed(self, text, image_path):
    '''Обрабатывает успешное распознавание текста'''
    self.ids.prompt_input.disabled = False
    self.ids.send_button.disabled = False

    self.ids.prompt_input.text = text
    self.ids.prompt_input.hint_text = self.texts['ocr_success']

    Clock.schedule_once(lambda dt: self.send_prompt(None), .5)
    Clock.schedule_once(lambda dt: self._restore_hint_text(), 3)


def on_image_processed_error(self, error_message):
    '''Обрабатывает ошибку распознавания'''
    self.ids.prompt_input.disabled = False
    self.ids.send_button.disabled = False
    self.ids.prompt_input.text = error_message
    self.ids.prompt_input.hint_text = self.texts.get('prompt_hint_text', '')
    Clock.schedule_once(lambda dt: self._restore_hint_text(), 3)


# Функции для работы с промптами
def show_prompts_dialog(self, instance):
    '''Показывает диалог добавления промпта'''
    current_chat_id = self.history_manager.chat_manager.current_chat_id
    current_prompt = self.prompt_manager.get_prompt(current_chat_id) or ''

    content = MDBoxLayout(
        orientation='vertical',
        spacing=dp(10),
        size_hint_y=None,
        height=dp(300),
        padding=dp(10)
    )

    self.prompt_input_field = MDTextField(
        text=current_prompt,
        hint_text=self.texts['prompt_input_field'],
        mode='rectangle',
        multiline=True,
        size_hint_y=None,
        height=dp(200),
        max_height=dp(200)
    )

    scroll_view = MDScrollView(
        size_hint_y=None,
        height=dp(220),
        do_scroll_x=False,
        do_scroll_y=True
    )
    scroll_view.add_widget(self.prompt_input_field)

    content.add_widget(scroll_view)

    buttons = [
        MDRaisedButton(
            text=self.texts['save_prompt_button'],
            text_color=(0, 1, 0, 1),
            md_bg_color=(0, 1, 0, .5),
            on_press=self.save_system_prompt
        ),
        MDRaisedButton(
            text=self.texts['delete_prompt_button'],
            text_color=(1, .5, 0, 1),
            md_bg_color=(1, .5, 0, .5),
            on_press=self.delete_system_prompt
        ),
        MDRaisedButton(
            text=self.texts['close_button'],
            text_color=(1, 0, 0, 1),
            md_bg_color=(1, 0, 0, .5),
            on_press=lambda instance: self.prompts_dialog.dismiss()
        )
    ]

    self.prompts_dialog = MDDialog(
        title=self.texts['prompt_dialog_title'],
        type='custom',
        content_cls=content,
        size_hint=(.9, None),
        height=dp(450),
        buttons=buttons
    )
    self.prompts_dialog.open()


def save_system_prompt(self, instance):
    '''Сохраняет системный промпт'''
    if not hasattr(self, 'prompt_input_field'):
        return

    prompt_text = self.prompt_input_field.text
    chat_id = self.history_manager.chat_manager.current_chat_id

    if self.prompt_manager.save_prompts(chat_id, prompt_text):
        if prompt_text and prompt_text.strip():
            self.ids.prompt_input.hint_text = self.texts['prompt_saved']
        else:
            self.ids.prompt_input.hint_text = self.texts['prompt_deleted']

        self.print_chat_name()
        Clock.schedule_once(lambda dt: self._restore_hint_text(), 3)
        if hasattr(self, 'prompts_dialog') and self.prompts_dialog:
            self.prompts_dialog.dismiss()
    else:
        self.ids.prompt_input.hint_text = self.texts['prompt_save_error']
        Clock.schedule_once(lambda dt: self._restore_hint_text(), 3)


def delete_system_prompt(self, instance):
    '''Удаляет системный промпт'''
    chat_id = self.history_manager.chat_manager.current_chat_id

    if self.prompt_manager.delete_prompt(chat_id):
        self.ids.prompt_input.hint_text = self.texts['prompt_deleted']
        self.print_chat_name()

        Clock.schedule_once(lambda dt: self._restore_hint_text(), 3)
        if hasattr(self, 'prompt_input_field'):
            self.prompt_input_field.text = ''
        if hasattr(self, 'prompts_dialog') and self.prompts_dialog:
            self.prompts_dialog.dismiss()
    else:
        self.ids.prompt_input.hint_text = self.texts['prompt_not_found']
        Clock.schedule_once(lambda dt: self._restore_hint_text(), 3)


def restore_hint_text(self):
    '''Восстанавливает стандартную подсказку'''
    if hasattr(self, 'texts'):
        self.ids.prompt_input.hint_text = self.texts['prompt_input']


# Функции для обновления интерфейса
def update_interface_language(self):
    '''Обновляет все тексты интерфейса в соответствии с текущим языком'''
    self.ids.prompt_input.hint_text = self.texts['prompt_input']

    if self.dialog:
        self.dialog.title = self.texts['dialog_title']
        self.dialog.text = self.texts['dialog_text']
        for button in self.dialog.buttons:
            if button.text in self.get_confirm_texts():
                button.text = self.texts['confirm_clear_button']
            elif button.text in self.get_cancel_texts():
                button.text = self.texts['cancel_clear_button']

    if hasattr(self, 'chats_dialog') and self.chats_dialog:
        self.chats_dialog.title = self.texts['chats_dialog_title']
        for button in self.chats_dialog.buttons:
            if button.text in self.get_close_texts():
                button.text = self.texts['close_button']
        refresh_chats_dialog(self)

    if hasattr(self, 'language_dialog') and self.language_dialog:
        self.language_dialog.title = self.texts['language_dialog']
        for button in self.language_dialog.buttons:
            if button.text in self.get_close_texts():
                button.text = self.texts['close_button']
