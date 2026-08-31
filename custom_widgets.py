# Импорт зависимостей
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDIconButton
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.image import AsyncImage

from syntax_highlighter import highlight_python_code, COLORS

# Создание класса сообщения
class Message(MDCard):
    def __init__(self, text='', align='center', role='user', **kwargs):
        super().__init__(**kwargs)

        # Установка параметров сообщения
        self.align = align
        self.role = role
        self.size_hint_x = None
        self.size_hint_y = None
        self.radius = [dp(10)]
        self.padding = [0, 0, 0, 0]
        self.width = Window.width * .8
        self.md_bg_color = (0, 0, 0, 0)

        self.main_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=self.spacing
        )
        self.main_layout.height = 0
        self.add_widget(self.main_layout)

        self.text_container = MDCard(
            size_hint=(1, None),
            size_hint_y=None,
            radius=self.radius,
            padding=[dp(15), dp(12), dp(15), dp(12)]
        )
        self.text_container.height = 0
        if role == 'user':
            self.text_container.md_bg_color = (0, 0, .9, 1)
        else:
            self.text_container.md_bg_color = (.11, .11, .11, 1)
        self.main_layout.add_widget(self.text_container)

        self.message_text = MDLabel(
            text=text,
            halign=align,
            font_size=dp(16),
            size_hint_y=None,
            text_size=(self.width - dp(30), None),
            markup=True
        )
        self.text_container.add_widget(self.message_text)

        self.copy_button = MDIconButton(
            icon='content-copy',
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'right': 1} if align == 'right' else {'left': 1},
            theme_icon_color='Custom',
            icon_color=(.5, .5, .5, .8),
            opacity=.5,
            on_press=self.copy_text
        )
        self.main_layout.add_widget(self.copy_button)

        self._update_pos_hint()

        self.message_text.bind(text=self._update_size)
        self.message_text.bind(texture_size=self._update_size)
        self.bind(width=self._update_size)

        Window.bind(size=self._on_window_resize)
        Clock.schedule_once(lambda dt: self._update_size(), 0)

    def copy_text(self, instance):
        '''Копирует текст сообщения в буфер обмена'''
        text = self.message_text.text
        if text:
            Clipboard.copy(text)
            self.copy_button.icon = 'check'
            self.copy_button.icon_color = (0, 1, 0, 1)
            Clock.schedule_once(self._reset_copy_button, 1)

    def _reset_copy_button(self, dt):
        '''Сбрасывает иконку кнопки копирования'''
        self.copy_button.icon = 'content-copy'
        self.copy_button.icon_color = (.5, .5, .5, .8)

    def _update_pos_hint(self):
        '''Обновляет позиционирование в зависимости от выравнивания'''
        if self.align == 'left':
            self.pos_hint = {'left': 1}
            self.message_text.halign = 'left'
        elif self.align == 'right':
            self.pos_hint = {'right': 1}
            self.message_text.halign = 'right'
        else:
            self.pos_hint = {'center_x': .5}
            self.message_text.halign = 'center'

    def _on_window_resize(self, instance, size):
        '''Обновляет ширину при изменении размера окна'''
        self.width = size[0] * .8
        self._update_size()

    def _update_size(self, *args):
        '''Обновляет размеры текстового поля'''
        self.message_text.text_size = (self.width - dp(30), None)
        self.message_text.texture_update()
        text_height = self.message_text.texture_size[1]
        self.message_text.height = text_height + dp(10)
        self.message_text.size_hint_y = None

        self.text_container.height = (
                self.message_text.height +
                self.text_container.padding[1] +
                self.text_container.padding[3]
        )
        self.text_container.size_hint_y = None

        self.main_layout.height = (
                self.text_container.height +
                self.copy_button.height +
                self.spacing
        )
        self.main_layout.size_hint_y = None

        new_height = self.main_layout.height
        if self.height != new_height:
            self.height = new_height
            self.size_hint_y = None
            if self.parent:
                if hasattr(self.parent, 'height'):
                    self.parent.height = self.parent.minimum_height

    def update_parent(self):
        '''Обновляет родительский контейнер'''
        if self.parent and self.parent.parent:
            container = self.parent
            if hasattr(container, 'height'):
                container.height = container.minimum_height
                if hasattr(container, 'parent') and hasattr(container.parent, 'height'):
                    container.parent.height = container.parent.minimum_height

    def set_align(self, align):
        '''Метод для изменения выравнивания после создания'''
        if align in ['left', 'right', 'center']:
            self.align = align
            self._update_pos_hint()

    def set_width(self, new_width):
        '''Устанавливает новую ширину сообщения'''
        if self.width != new_width:
            self.width = new_width
            self._update_size()

    def force_update(self):
        '''Принудительно обновляет сообщение'''
        self._update_size()
        if self.parent:
            if hasattr(self.parent, 'height'):
                self.parent.height = self.parent.minimum_height


# Создание класса картинки
class ImageMessage(MDCard):
    def __init__(self, image_path: str, align='left', role='assistant', **kwargs):
        super().__init__(**kwargs)

        self.align = align
        self.role = role
        self.image_path = image_path
        self.size_hint_x = None
        self.size_hint_y = None
        self.radius = [dp(10)]
        self.padding = [0, 0, 0, 0]
        self.width = Window.width * .8
        self.md_bg_color = (0, 0, 0, 0)

        self.main_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5)
        )
        self.main_layout.height = 0
        self.add_widget(self.main_layout)

        self.image_container = MDCard(
            size_hint=(1, None),
            size_hint_y=None,
            radius=self.radius,
            padding=[dp(5), dp(5), dp(5), dp(5)],
            md_bg_color=(.11, .11, .11, 1)
        )
        self.image_container.height = 0
        self.main_layout.add_widget(self.image_container)

        self.image = AsyncImage(
            source=image_path,
            size_hint=(1, None),
            keep_ratio=True,
            allow_stretch=True
        )
        self.image.height = Window.width * .6
        self.image_container.add_widget(self.image)

        self.image.bind(texture=self._update_size)
        self.image.bind(size=self._update_size)

        self.bind(width=self._update_size)
        Window.bind(size=self._on_window_resize)

        self._update_pos_hint()

        Clock.schedule_once(lambda dt: self._update_size(), .1)
        Clock.schedule_once(lambda dt: self._update_size(), .3)
        Clock.schedule_once(lambda dt: self._update_size(), .5)

    def _update_pos_hint(self):
        '''Обновляет позиционирование в зависимости от выравнивания'''
        if self.align == 'left':
            self.pos_hint = {'left': 1}
        elif self.align == 'right':
            self.pos_hint = {'right': 1}
        else:
            self.pos_hint = {'center_x': .5}

    def _on_window_resize(self, instance, size):
        '''Обновляет размер при изменении окна'''
        self.width = size[0] * .8
        Clock.schedule_once(lambda dt: self._update_size(), .1)

    def _update_size(self, *args):
        '''Обновляет размеры после загрузки изображения'''
        if self.image.texture:
            img_width = self.image.texture.width
            img_height = self.image.texture.height

            current_width = self.width or Window.width * .8
            max_width = current_width - dp(20)

            if max_width <= 0:
                max_width = Window.width * .7

            if img_width > max_width:
                ratio = max_width / img_width
                new_height = img_height * ratio
            else:
                new_height = img_height

            max_height = Window.height * .5
            if new_height > max_height:
                new_height = max_height

            self.image.height = new_height
            self.image.size_hint_y = None

            self.image_container.height = new_height + dp(10)
            self.image_container.size_hint_y = None

            self.main_layout.height = self.image_container.height
            self.height = self.main_layout.height

            if self.parent:
                if hasattr(self.parent, 'height'):
                    self.parent.height = self.parent.minimum_height


# Создание класса кодового сообщения
class CodeArea(MDCard):
    '''Виджет для отображения кода с подсветкой синтаксиса'''

    def __init__(self, code='', align='left', role='assistant', **kwargs):
        super().__init__(**kwargs)

        self.align = align
        self.role = role
        self.code = code
        self.size_hint_x = None
        self.size_hint_y = None
        self.radius = [dp(5)]
        self.padding = [0, 0, 0, 0]
        self.width = Window.width * .8
        self.md_bg_color = (0, 0, 0, 0)

        self.main_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=0
        )
        self.main_layout.height = 0
        self.add_widget(self.main_layout)

        self.header = MDCard(
            size_hint=(1, None),
            size_hint_y=None,
            height=dp(30),
            radius=[dp(5), dp(5), 0, 0],
            padding=[dp(10), dp(5)],
            md_bg_color=(.15, .15, .2, 1)
        )

        self.lang_label = MDLabel(
            text='Code',
            font_size=dp(12),
            halign='left',
            color=(.5, .5, .5, 1),
            size_hint_x=.8
        )
        self.header.add_widget(self.lang_label)

        self.copy_button = MDIconButton(
            icon='content-copy',
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'right': -1, 'y': -.5},
            theme_icon_color='Custom',
            icon_color=(.5, .5, .5, .8),
            opacity=.5,
            on_press=self.copy_code
        )
        self.header.add_widget(self.copy_button)
        self.main_layout.add_widget(self.header)

        self.code_scroll = MDScrollView(
            size_hint=(1, None),
            size_hint_y=None,
            height=dp(200),
            do_scroll_x=True,
            do_scroll_y=True
        )
        self.main_layout.add_widget(self.code_scroll)

        self.code_container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(2),
            padding=[dp(10), dp(10), dp(10), dp(10)],
            size_hint_x=None
        )
        self.code_container.height = 0
        self.code_container.width = 0
        self.code_scroll.add_widget(self.code_container)

        self._update_pos_hint()

        Clock.schedule_once(lambda dt: self._build_code(), .1)

        Window.bind(size=self._on_window_resize)

    def copy_code(self, instance):
        '''Копирует код в буфер обмена'''
        if self.code:
            Clipboard.copy(self.code)
            self.copy_button.icon = 'check'
            self.copy_button.icon_color = (0, 1, 0, 1)
            Clock.schedule_once(self._reset_copy_button, 1)

    def _reset_copy_button(self, dt):
        '''Сбрасывает иконку кнопки копирования'''
        self.copy_button.icon = 'content-copy'
        self.copy_button.icon_color = (.5, .5, .5, .8)

    def _update_pos_hint(self):
        '''Обновляет позиционирование'''
        if self.align == 'left':
            self.pos_hint = {'left': 1}
        elif self.align == 'right':
            self.pos_hint = {'right': 1}
        else:
            self.pos_hint = {'center_x': .5}

    def _on_window_resize(self, instance, size):
        '''Обновляет ширину при изменении размера окна'''
        self.width = size[0] * .8
        Clock.schedule_once(lambda dt: self._build_code(), .1)

    def _build_code(self):
        '''Строит отображение кода с подсветкой'''
        self.code_container.clear_widgets()

        lines = self.code.split('\n')

        max_line_width = 0
        line_boxes = []
        temp_width = self.width - dp(40)

        for line in lines:
            line_box = MDBoxLayout(
                size_hint_y=None,
                height=dp(24),
                spacing=0,
                size_hint_x=None
            )
            line_width = 0

            if not line.strip():
                empty_label = MDLabel(
                    text=' ',
                    font_size=dp(14),
                    size_hint_x=None,
                    width=dp(10),
                    color=(.9, .9, .9, 1),
                    text_size=(None, None),
                    shorten=False
                )
                line_box.add_widget(empty_label)
                line_width = dp(10)
            else:
                tokens = highlight_python_code(line)
                for token in tokens:
                    label = Label(
                        text=token['text'],
                        font_size=dp(14),
                        size_hint_x=None,
                        width=0,
                        halign='left',
                        valign='middle',
                        color=token['color'],
                        text_size=(None, None),
                        shorten=False,
                        markup=False
                    )
                    label.texture_update()
                    label_width = label.texture_size[0] + dp(2)
                    label.width = label_width
                    line_width += label_width
                    line_box.add_widget(label)

            line_box.width = max(line_width, temp_width)
            line_box.size_hint_x = None
            line_boxes.append(line_box)

            if line_width > max_line_width:
                max_line_width = line_width

        for line_box in line_boxes:
            self.code_container.add_widget(line_box)

        self.code_container.width = max(max_line_width, temp_width)
        self.code_container.size_hint_x = None

        Clock.schedule_once(lambda dt: self._update_size(), .1)

    def _update_size(self, *args):
        '''Обновляет размеры виджета'''
        if not self.code_container.children:
            return

        total_height = 0
        for child in self.code_container.children:
            total_height += child.height

        total_height += dp(20)
        self.code_container.height = total_height
        self.code_container.size_hint_y = None

        max_height = Window.height * .4
        scroll_height = min(total_height, max_height)
        self.code_scroll.height = max(dp(100), scroll_height)
        self.code_scroll.size_hint_y = None

        self.main_layout.height = self.header.height + self.code_scroll.height
        self.main_layout.size_hint_y = None
        self.height = self.main_layout.height
        self.size_hint_y = None

        if self.parent:
            if hasattr(self.parent, 'height'):
                self.parent.height = self.parent.minimum_height
                if hasattr(self.parent, 'parent') and hasattr(self.parent.parent, 'height'):
                    self.parent.parent.height = self.parent.parent.minimum_height

        Clock.schedule_once(lambda dt: self._scroll_to_top(), .05)

    def _scroll_to_top(self):
        '''Прокручивает к началу кода'''
        if self.code_scroll:
            self.code_scroll.scroll_y = 1

    def set_width(self, new_width):
        '''Устанавливает новую ширину'''
        if self.width != new_width:
            self.width = new_width
            self._build_code()

    def force_update(self):
        '''Принудительно обновляет виджет'''
        self._build_code()
        self._update_size()
        if self.parent:
            if hasattr(self.parent, 'height'):
                self.parent.height = self.parent.minimum_height
