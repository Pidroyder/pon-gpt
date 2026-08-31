# Импорт зависимостей
import os
import uuid
import mimetypes

from kivy.clock import Clock


def _log(msg):
    try:
        from android.storage import app_storage_path
        with open(os.path.join(app_storage_path(), 'picker.log'), 'a') as file:
            file.write(msg + '\n')
    except Exception:
        pass


def _copy_uri_to_cache(uri):
    '''Копирует выбранное изображение из системного URI в папку приложения'''
    dest_dir = None
    try:
        from jnius import autoclass
        from android.storage import app_storage_path

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        resolver = PythonActivity.mActivity.getContentResolver()

        mime = resolver.getType(uri)
        ext = mimetypes.guess_extension(mime) if mime else None
        if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'):
            ext = '.jpg'

        dest_dir = os.path.join(app_storage_path(), 'picked')
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        dest = os.path.join(dest_dir, f'image_{uuid.uuid4().hex[:8]}{ext}')

        total = 0
        try:
            PFD = autoclass('android.os.ParcelFileDescriptor')
            pfd = resolver.openFileDescriptor(uri, 'r')
            fd = pfd.detachFd()
            with os.fdopen(fd, 'rb') as fsrc:
                with open(dest, 'wb') as fdst:
                    while True:
                        chunk = fsrc.read(65536)
                        if not chunk:
                            break
                        fdst.write(chunk)
                        total += len(chunk)
            try:
                pfd.close()
            except Exception:
                pass
            _log(f'pick_image: fd-copy ok, {total} bytes')
        except Exception as e:
            _log(f'pick_image: fd-copy failed ({e}), falling back to stream')
            stream = resolver.openInputStream(uri)
            if stream is None:
                _log('pick_image: stream is None')
                return None, dest_dir
            chunk_list = []
            while True:
                break_ = stream.read()
                if break_ < 0:
                    break
                chunk_list.append(break_)
            with open(dest, 'wb') as file:
                file.write(bytes(chunk_list))
            total = len(chunk_list)
            try:
                stream.close()
            except Exception:
                pass

        if total == 0:
            _log('pick_image: copied 0 bytes')
            return None, dest_dir

        _log(f'pick_image: copied {total} bytes to {dest}')
        return dest, None
    except Exception as e:
        _log(f'pick_image: URI copy error: {e}')
        return None, dest_dir


def pick_image(on_result):
    '''Открывает системный выбор изображения и возвращает путь через callback'''
    try:
        from jnius import autoclass
        from android import activity as android_activity

        _log('pick_image: starting')

        Intent = autoclass('android.content.Intent')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Activity = autoclass('android.app.Activity')

        def on_result_ready(request_code, result_code, intent):
            _log(f'pick_image: result code={result_code}, req={request_code}')
            try:
                android_activity.unbind(on_activity_result=on_result_ready)
            except Exception:
                pass

            if request_code != 7351:
                _log(f'pick_image: wrong request_code {request_code}')
                return

            if result_code != Activity.RESULT_OK or intent is None:
                _log(f'pick_image: cancelled or null intent')
                Clock.schedule_once(lambda dt: on_result(None), 0)
                return

            uri = intent.getData()
            if uri is None:
                _log('pick_image: uri is None')
                Clock.schedule_once(lambda dt: on_result(None), 0)
                return

            _log(f'pick_image: got uri={uri}')
            path, _err = _copy_uri_to_cache(uri)
            _log(f'pick_image: path={path}')
            Clock.schedule_once(lambda dt: on_result(path), 0)

        android_activity.bind(on_activity_result=on_result_ready)

        intent = Intent(Intent.ACTION_GET_CONTENT)
        intent.setType('image/*')
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

        current_activity = PythonActivity.mActivity
        current_activity.startActivityForResult(intent, 7351)
        _log('pick_image: startActivityForResult called')
    except Exception as e:
        _log(f'pick_image: exception: {e}')
        Clock.schedule_once(lambda dt: on_result(None), 0)
