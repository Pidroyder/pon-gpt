# Импорт зависимостей
import threading

from kivy.clock import Clock
from kivy.utils import platform


class VoiceInput:
    '''Голосовой ввод'''
    def __init__(self, callback=None):
        self.callback = callback
        self._impl = None

        if platform == 'android':
            try:
                from android_voice_input import AndroidVoiceInput
                self._impl = AndroidVoiceInput()
            except Exception as e:
                raise RuntimeError(f'Android voice error: {e}')
        else:
            try:
                import speech_recognition as sr
                self._impl = _DesktopVoiceInput(sr)
            except Exception as e:
                raise RuntimeError(f'Voice init error: {e}')

    def start_recording(self, callback=None):
        if callback:
            self.callback = callback
        self._impl.start_recording(callback or self.callback)

    def stop_recording(self):
        if self._impl:
            self._impl.stop_recording()


class _DesktopVoiceInput:
    def __init__(self, sr):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.energy_threshold = 3000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = .8
        self.is_recording = False
        self.audio_data = None
        self.callback = None
        self._sr = sr

    def start_recording(self, callback):
        if self.is_recording:
            return
        self.callback = callback
        self.is_recording = True
        thread = threading.Thread(target=self._record)
        thread.daemon = True
        thread.start()

    def _record(self):
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                self.audio_data = audio
                Clock.schedule_once(lambda dt: self._recognize(), 0)
        except self._sr.WaitTimeoutError:
            Clock.schedule_once(lambda dt: self._err('Timeout exceeded'), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._err(str(e)), 0)
        finally:
            self.is_recording = False

    def _recognize(self):
        if not self.audio_data:
            self._err('No audio data')
            return
        try:
            text = self.recognizer.recognize_google(self.audio_data, language='ru-RU')
            if self.callback:
                Clock.schedule_once(lambda dt: self.callback(text), 0)
        except self._sr.UnknownValueError:
            self._err('Could not recognize speech')
        except self._sr.RequestError as e:
            self._err(f'Service error: {e}')
        except Exception as e:
            self._err(str(e))

    def _err(self, msg):
        if self.callback:
            Clock.schedule_once(lambda dt: self.callback(None, msg), 0)

    def stop_recording(self):
        self.is_recording = False
