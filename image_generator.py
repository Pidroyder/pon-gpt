# Импорт зависимостей
import os
import asyncio
from datetime import datetime

from picwish import PicWish, T2ITheme, T2IQuality, T2ISize
from kivy.utils import platform

if platform == 'android':
    try:
        from android.storage import app_storage_path
    except:
        app_storage_path = None


# Функция отрисовки изображения
async def draw_image(prompt: str, file_path: str):
    '''Рисует картинку'''
    picwish = PicWish()
    results = await picwish.text_to_image(
        prompt=prompt,
        theme=T2ITheme.GENERAL,
        size=T2ISize.FHD_1_1,
        batch_size=1,
        quality=T2IQuality.HIGH
    )
    await results[0].download(file_path)


# Функция создания картинки
def create_image(prompt: str, filename: str) -> str:
    '''Рисует и сохраняет картинку'''
    try:
        images_dir = get_images_dir()
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        file_path = os.path.join(images_dir, f'{filename}.png')

        asyncio.run(draw_image(prompt, file_path))

        return file_path
    except:
        return None


# Функция получения пути к папке с картинками
def get_images_dir() -> str:
    if platform == 'android':
        return os.path.join(app_storage_path(), 'images')
    else:
        return os.path.join(os.path.dirname(__file__), 'images')


# Функция удаления изображений
def delete_images(image_path: str):
    '''Удаляет изображение по пути'''
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            return True
        else:
            return False
    except:
        return False


# Функция удаления всех изображений чата
def delete_chat_images(messages: list):
    '''Удаляет все изображения из списка сообщений'''
    deleted_count = 0
    for msg in messages:
        if msg.get('msg_type') == 'image':
            image_path = msg.get('content')
            if image_path and delete_images(image_path):
                deleted_count += 1
    return deleted_count
