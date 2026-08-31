# Импорт зависимостей
import os

from kivy.utils import platform

if platform == 'android':
    try:
        from android.storage import app_storage_path
    except Exception:
        app_storage_path = None
else:
    app_storage_path = None


# Кэш Java-класса OcrBridge
_OcrBridge = None
if platform == 'android':
    try:
        from jnius import autoclass
        _OcrBridge = autoclass('org.pongpt.OcrBridge')
    except Exception:
        _OcrBridge = None


# Функция распознавания текста с картинки
def get_text_from_image(filename: str) -> str:
    '''Распознает текст с изображения'''
    file_path = os.path.join(_get_sent_images_dir_path(), filename)
    if not os.path.exists(file_path):
        return ''

    if platform == 'android':
        return _get_text_mlkit(file_path)

    try:
        return _get_text_easyocr(file_path)
    except Exception:
        return ''


def _get_text_mlkit(file_path: str) -> str:
    '''Распознаёт текст через Google ML Kit'''
    from jnius import autoclass

    def _ocr_log(msg):
        try:
            if platform == 'android':
                from android.storage import app_storage_path
                with open(os.path.join(app_storage_path(), 'ocr.log'), 'a') as f:
                    f.write(str(msg) + '\n')
        except Exception:
            pass

    def jvm_detail(e, full=False):
        jclass = '?'
        inner = ''
        try:
            je = getattr(e, 'java_exception', None)
            if je is not None:
                try:
                    jclass = je.getClass().getName()
                except Exception:
                    jclass = '?'
        except Exception:
            pass
        try:
            im = getattr(e, 'innermessage', None)
            if im:
                inner = f' :: {im}'
        except Exception:
            pass
        raw = str(e) if not jclass or jclass == '?' else None
        if full:
            return f'JVM exception: {jclass}{inner}' + (f' ({raw})' if raw else '')
        if not jclass or jclass == '?':
            return f'JVM exception: {raw or "?"}'
        return f'JVM exception: {jclass}'

    try:
        _ocr_log('[OCR] start')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity

        bridge = _OcrBridge
        if bridge is None:
            bridge = autoclass('org.pongpt.OcrBridge')
        if bridge is None:
            raise RuntimeError('OcrBridge class not loaded')

        File = autoclass('java.io.File')
        Uri = autoclass('android.net.Uri')
        uri = Uri.fromFile(File(file_path))

        text = bridge.process(activity, uri)
        text = (str(text or '')).strip()
        _ocr_log(f'[OCR] ok text_len={len(text)}')
        if not text:
            return ''
        return f'The text at photo: {text}'
    except BaseException as e:
        _ocr_log(f'[OCR init] {jvm_detail(e, full=True)}')
        raise RuntimeError(jvm_detail(e)) from e


def _get_text_easyocr(file_path: str) -> str:
    '''Распознаёт текст через easyocr (десктоп)'''
    from PIL import Image
    import numpy
    import cv2

    img = Image.open(file_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    img_array = numpy.array(img)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    import easyocr
    reader = easyocr.Reader(['ru', 'en'], gpu=False, verbose=False)

    result = reader.readtext(img_bgr, detail=0)
    text = ' '.join(result)

    return f'The text at photo: {text.strip()}'


# Функция получения пути к папке с изображениями
def _get_sent_images_dir_path(dir_name='sent_images') -> str:
    if platform == 'android' and app_storage_path:
        path = os.path.join(app_storage_path(), dir_name)
    else:
        path = os.path.join(os.path.dirname(__file__), dir_name)
    return path


# Создает папку с отправленными изображениями если ее нет
def _ensure_sent_images_dir() -> None:
    path = _get_sent_images_dir_path()
    if not os.path.exists(path):
        os.makedirs(path)


# Функция удаления отправленного изображения
def delete_sent_image(filename: str) -> bool:
    '''Удаляет отправленное изображение'''
    try:
        file_path = os.path.join(_get_sent_images_dir_path(), filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False
