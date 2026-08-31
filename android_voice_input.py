# Импорт зависимостей
from kivy.clock import Clock
from kivy.utils import platform


class AndroidVoiceInput:
    '''Голосовой ввод через системный диалог Android'''
    def __init__(self):
        self._is_listening = False
        self._callback = None
        self._bound = False
        self._ensure_available()

    def _ensure_available(self):
        from jnius import autoclass
        SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
        if SpeechRecognizer.isRecognitionAvailable(
                autoclass('org.kivy.android.PythonActivity').mActivity) is False:
            raise RuntimeError('Recognition not available')

    def start_recording(self, callback):
        '''Открывает системный диалог распознавания речи'''
        if self._is_listening:
            return

        self._callback = callback
        self._is_listening = True

        try:
            from jnius import autoclass
            from android import activity as android_activity

            Intent = autoclass('android.content.Intent')
            RecognizerIntent = autoclass('android.speech.RecognizerIntent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Activity = autoclass('android.app.Activity')

            def on_voice_result(request_code, result_code, intent):
                try:
                    android_activity.unbind(on_activity_result=on_voice_result)
                except Exception:
                    pass
                self._is_listening = False
                cb = self._callback
                if request_code != 7352:
                    return
                if result_code != Activity.RESULT_OK or intent is None:
                    if cb:
                        Clock.schedule_once(lambda dt: cb(None, 'Cancelled'), 0)
                    return
                try:
                    matches = intent.getStringArrayListExtra(
                        RecognizerIntent.EXTRA_RESULTS)
                    if matches and matches.size() > 0:
                        text = str(matches.get(0))
                        if cb:
                            Clock.schedule_once(lambda dt, t=text: cb(t), 0)
                    else:
                        if cb:
                            Clock.schedule_once(lambda dt: cb(None, 'No speech recognized'), 0)
                except Exception as e:
                    if cb:
                        Clock.schedule_once(lambda dt: cb(None, str(e)), 0)

            android_activity.bind(on_activity_result=on_voice_result)
            self._bound = True

            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, 'ru-RU')
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, 'ru-RU')
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, 'Говорите...')

            current_activity = PythonActivity.mActivity
            current_activity.startActivityForResult(intent, 7352)
        except Exception as e:
            self._is_listening = False
            if self._callback:
                Clock.schedule_once(lambda dt: self._callback(None, str(e)), 0)

    def stop_recording(self):
        '''Останавливает запись'''
        self._is_listening = False

    def destroy(self):
        '''Освобождает ресурсы'''
        self._is_listening = False
