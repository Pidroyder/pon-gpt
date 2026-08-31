# Импорт зависимостей
import os
from kivy.utils import platform

if platform == 'android':
    try:
        from android.storage import app_storage_path
    except:
        app_storage_path = None


# Класс управления языками приложения
class LanguageManager:
    def __init__(self, lang_file='language.txt'):
        self.lang_file = lang_file
        self._available_languages = {
            'RU': 'Русский',
            'EN': 'English',
            'FR': 'Français',
            'ZH': 'Pinyin',
            'ES': 'Español',
            'DE': 'Deutsch',
            'PT': 'Português'
        }
        self._translations = self.load_translations()

    def load_translations(self):
        '''Загружает все переводы'''
        return {
            'RU': {
                'prompt_input': 'Ваш запрос...',
                'prompt_input_field': 'Введите системный промпт...',
                'loading_message': 'Думаю...',
                'dialog_title': 'Вы действительно хотите очистить данный чат?',
                'dialog_text': 'Данное действие нельзя будет отменить',
                'confirm_clear_button': 'Да',
                'cancel_clear_button': 'Отмена',
                'new_chat_item': '+ Новый чат',
                'no_chats_item': 'Нет созданных чатов',
                'chats_dialog_title': 'Ваши чаты',
                'text_field': 'Введите новое название',
                'rename_dialog_title': 'Переименовать чат',
                'cancel_rename_button': 'Отмена',
                'confirm_rename_button': 'Сохранить',
                'language_dialog': 'Выберите язык',
                'prompt_dialog_title': 'Системный промпт',
                'save_prompt_button': 'Сохранить',
                'delete_prompt_button': 'Удалить',
                'response_error': 'Ошибка получения ответа',
                'request_error': 'Ошибка запроса',
                'image_error': 'Ошибка генерации изображения',
                'voice_error': 'Ошибка записи голоса',
                'ocr_error': 'Ошибка распознавания текста',
                'prompt_saved': 'Промпт сохранен',
                'prompt_deleted': 'Промпт удален',
                'prompt_save_error': 'Ошибка сохранения промпта',
                'prompt_not_found': 'Промпт не найден',
                'prompt_delete_error': 'Ошибка удаления промпта',
                'close_button': 'Закрыть',
                'select_button': 'Выбрать',
                'cancel_button': 'Отмена',
                'ocr_processing': 'Распознавание текста на изображении...',
                'ocr_success': 'Текст распознан!',
                'ocr_no_text': 'Текст не найден на изображении',
                'ocr_error_message': 'Ошибка распознавания',
                'voice_recording': 'Запись...',
                'voice_error_timeout': 'Превышено время ожидания',
                'voice_error_unknown': 'Не удалось распознать речь',
                'voice_error_service': 'Ошибка сервиса распознавания',
                'voice_error_general': 'Ошибка распознавания',
                'code_label': 'Code',
                'code_copy': 'Копировать код',
                'code_copied': 'Код скопирован',
                'image_select_title': 'Выберите изображение',
                'image_processed': 'Изображение обработано',
                'image_saved': 'Изображение сохранено',
                'system_prompt_instruction': 'Введите системный промпт для текущего чата.\nОн будет использоваться для всех последующих запросов.'
            },
            'EN': {
                'prompt_input': 'Your query...',
                'prompt_input_field': 'Enter system prompt...',
                'loading_message': 'Thinking...',
                'dialog_title': 'Are you sure you want to clear this chat?',
                'dialog_text': 'This action cannot be undone',
                'confirm_clear_button': 'Yes',
                'cancel_clear_button': 'Cancel',
                'new_chat_item': '+ New chat',
                'no_chats_item': 'No chats created',
                'chats_dialog_title': 'Your chats',
                'text_field': 'Enter new name',
                'rename_dialog_title': 'Rename chat',
                'cancel_rename_button': 'Cancel',
                'confirm_rename_button': 'Save',
                'language_dialog': 'Choose language',
                'prompt_dialog_title': 'System prompt',
                'save_prompt_button': 'Save',
                'delete_prompt_button': 'Delete',
                'response_error': 'Response error',
                'request_error': 'Query error',
                'image_error': 'Image generation error',
                'voice_error': 'Voice recording error',
                'ocr_error': 'Text recognition error',
                'prompt_saved': 'Prompt saved',
                'prompt_deleted': 'Prompt deleted',
                'prompt_save_error': 'Error saving prompt',
                'prompt_not_found': 'Prompt not found',
                'prompt_delete_error': 'Error deleting prompt',
                'close_button': 'Close',
                'select_button': 'Select',
                'cancel_button': 'Cancel',
                'ocr_processing': 'Recognizing text from image...',
                'ocr_success': 'Text recognized!',
                'ocr_no_text': 'No text found on image',
                'ocr_error_message': 'Recognition error',
                'voice_recording': 'Recording...',
                'voice_error_timeout': 'Timeout exceeded',
                'voice_error_unknown': 'Could not recognize speech',
                'voice_error_service': 'Recognition service error',
                'voice_error_general': 'Recognition error',
                'code_label': 'Code',
                'code_copy': 'Copy code',
                'code_copied': 'Code copied',
                'image_select_title': 'Select image',
                'image_processed': 'Image processed',
                'image_saved': 'Image saved',
                'system_prompt_instruction': 'Enter a system prompt for the current chat.\nIt will be used for all subsequent queries.'
            },
            'FR': {
                'prompt_input': 'Votre requête...',
                'prompt_input_field': 'Saisissez l\'invite système...',
                'loading_message': 'Réflexion...',
                'dialog_title': 'Voulez-vous vraiment effacer cette conversation ?',
                'dialog_text': 'Cette action est irréversible',
                'confirm_clear_button': 'Oui',
                'cancel_clear_button': 'Annuler',
                'new_chat_item': '+ Nouvelle conversation',
                'no_chats_item': 'Aucune conversation créée',
                'chats_dialog_title': 'Vos conversations',
                'text_field': 'Entrez un nouveau nom',
                'rename_dialog_title': 'Renommer la conversation',
                'cancel_rename_button': 'Annuler',
                'confirm_rename_button': 'Enregistrer',
                'language_dialog': 'Choisissez la langue',
                'prompt_dialog_title': 'Invite système',
                'save_prompt_button': 'Enregistrer',
                'delete_prompt_button': 'Supprimer',
                'response_error': 'Erreur lors de la réception de la réponse',
                'request_error': 'Erreur de requête',
                'image_error': 'Erreur de génération d\'image',
                'voice_error': 'Erreur d\'enregistrement vocal',
                'ocr_error': 'Erreur de reconnaissance de texte',
                'prompt_saved': 'Invite enregistrée',
                'prompt_deleted': 'Invite supprimée',
                'prompt_save_error': 'Erreur d\'enregistrement',
                'prompt_not_found': 'Invite non trouvée',
                'prompt_delete_error': 'Erreur de suppression',
                'close_button': 'Fermer',
                'select_button': 'Sélectionner',
                'cancel_button': 'Annuler',
                'ocr_processing': 'Reconnaissance du texte sur l\'image...',
                'ocr_success': 'Texte reconnu !',
                'ocr_no_text': 'Aucun texte trouvé sur l\'image',
                'ocr_error_message': 'Erreur de reconnaissance',
                'voice_recording': 'Enregistrement...',
                'voice_error_timeout': 'Délai dépassé',
                'voice_error_unknown': 'Impossible de reconnaître la parole',
                'voice_error_service': 'Erreur du service de reconnaissance',
                'voice_error_general': 'Erreur de reconnaissance',
                'code_label': 'Code',
                'code_copy': 'Copier le code',
                'code_copied': 'Code copié',
                'image_select_title': 'Sélectionner une image',
                'image_processed': 'Image traitée',
                'image_saved': 'Image enregistrée',
                'system_prompt_instruction': 'Saisissez une invite système pour la conversation actuelle.\nElle sera utilisée pour toutes les requêtes suivantes.'
            },
            'ZH': {
                'prompt_input': 'Nin de tiwen...',
                'prompt_input_field': 'Shuru xitong tishi...',
                'loading_message': 'Xiang...',
                'dialog_title': 'Nin queding yao qingchu ci liao tian ma?',
                'dialog_text': 'Ci caozuo wufa chexiao',
                'confirm_clear_button': 'Queding',
                'cancel_clear_button': 'Quxiao',
                'new_chat_item': '+ Xin liao tian',
                'no_chats_item': 'Meiyou chuangjian de liao tian',
                'chats_dialog_title': 'Nin de liao tian',
                'text_field': 'Shuru xin mingcheng',
                'rename_dialog_title': 'Chong mingming liao tian',
                'cancel_rename_button': 'Quxiao',
                'confirm_rename_button': 'Bao cun',
                'language_dialog': 'Xuanze yuyan',
                'prompt_dialog_title': 'Xitong tishi',
                'save_prompt_button': 'Bao cun',
                'delete_prompt_button': 'Shanchu',
                'response_error': 'Huoqu cuowu',
                'request_error': 'Qingqiu cuowu',
                'image_error': 'Image generation error',
                'voice_error': 'Yuyin jilu cuowu',
                'ocr_error': 'Wenzi shibie cuowu',
                'prompt_saved': 'Tishi yibao cun',
                'prompt_deleted': 'Tishi yishanchu',
                'prompt_save_error': 'Baocun shibai',
                'prompt_not_found': 'Weizhaodao tishi',
                'prompt_delete_error': 'Shanchu shibai',
                'close_button': 'Guanbi',
                'select_button': 'Xuanze',
                'cancel_button': 'Quxiao',
                'ocr_processing': 'Zhengzai shibie tuwen...',
                'ocr_success': 'Shibie chenggong!',
                'ocr_no_text': 'Weizhaodao wenzi',
                'ocr_error_message': 'Shibie cuowu',
                'voice_recording': 'Luyin zhong...',
                'voice_error_timeout': 'Chaoshi',
                'voice_error_unknown': 'Wufa shibie yuyin',
                'voice_error_service': 'Fuwu cuowu',
                'voice_error_general': 'Shibie cuowu',
                'code_label': 'Daima',
                'code_copy': 'Fuzhi daima',
                'code_copied': 'Daima yifuzhi',
                'image_select_title': 'Xuanze tupian',
                'image_processed': 'Tupian yichuli',
                'image_saved': 'Tupian yibaocun',
                'system_prompt_instruction': 'Wei dangqian liaotian shuru xitong tishi.\nJiang yongyu suoyou houxu tiwen.'
            },
            'ES': {
                'prompt_input': 'Su consulta...',
                'prompt_input_field': 'Ingrese el mensaje del sistema...',
                'loading_message': 'Pensando...',
                'dialog_title': 'Está seguro de que desea borrar este chat?',
                'dialog_text': 'Esta acción no se puede deshacer',
                'confirm_clear_button': 'Sí',
                'cancel_clear_button': 'Cancelar',
                'new_chat_item': '+ Nuevo chat',
                'no_chats_item': 'No hay chats creados',
                'chats_dialog_title': 'Sus chats',
                'text_field': 'Ingrese un nuevo nombre',
                'rename_dialog_title': 'Renombrar chat',
                'cancel_rename_button': 'Cancelar',
                'confirm_rename_button': 'Guardar',
                'language_dialog': 'Seleccionar idioma',
                'prompt_dialog_title': 'Mensaje del sistema',
                'save_prompt_button': 'Guardar',
                'delete_prompt_button': 'Eliminar',
                'response_error': 'Error al obtener respuesta',
                'request_error': 'Error de solicitud',
                'image_error': 'Error de generación de imagen',
                'voice_error': 'Error de grabación de voz',
                'ocr_error': 'Error de reconocimiento de texto',
                'prompt_saved': 'Mensaje guardado',
                'prompt_deleted': 'Mensaje eliminado',
                'prompt_save_error': 'Error al guardar',
                'prompt_not_found': 'Mensaje no encontrado',
                'prompt_delete_error': 'Error al eliminar',
                'close_button': 'Cerrar',
                'select_button': 'Seleccionar',
                'cancel_button': 'Cancelar',
                'ocr_processing': 'Reconociendo texto de la imagen...',
                'ocr_success': 'Texto reconocido!',
                'ocr_no_text': 'No se encontró texto',
                'ocr_error_message': 'Error de reconocimiento',
                'voice_recording': 'Grabando...',
                'voice_error_timeout': 'Tiempo agotado',
                'voice_error_unknown': 'No se pudo reconocer',
                'voice_error_service': 'Error del servicio',
                'voice_error_general': 'Error de reconocimiento',
                'code_label': 'Código',
                'code_copy': 'Copiar código',
                'code_copied': 'Código copiado',
                'image_select_title': 'Seleccionar imagen',
                'image_processed': 'Imagen procesada',
                'image_saved': 'Imagen guardada',
                'system_prompt_instruction': 'Ingrese un mensaje del sistema para el chat actual.\nSe utilizará para todas las consultas posteriores.'
            },
            'DE': {
                'prompt_input': 'Ihre Anfrage...',
                'prompt_input_field': 'Geben Sie den System-Prompt ein...',
                'loading_message': 'Denken...',
                'dialog_title': 'Möchten Sie diesen Chat wirklich löschen?',
                'dialog_text': 'Diese Aktion kann nicht rückgängig gemacht werden',
                'confirm_clear_button': 'Ja',
                'cancel_clear_button': 'Abbrechen',
                'new_chat_item': '+ Neuer Chat',
                'no_chats_item': 'Keine Chats erstellt',
                'chats_dialog_title': 'Ihre Chats',
                'text_field': 'Neuen Namen eingeben',
                'rename_dialog_title': 'Chat umbenennen',
                'cancel_rename_button': 'Abbrechen',
                'confirm_rename_button': 'Speichern',
                'language_dialog': 'Sprache wählen',
                'prompt_dialog_title': 'System-Prompt',
                'save_prompt_button': 'Speichern',
                'delete_prompt_button': 'Löschen',
                'response_error': 'Fehler beim Abrufen der Antwort',
                'request_error': 'Anfragefehler',
                'image_error': 'Fehler bei der Bildgenerierung',
                'voice_error': 'Fehler bei der Sprachaufnahme',
                'ocr_error': 'Fehler bei der Texterkennung',
                'prompt_saved': 'Prompt gespeichert',
                'prompt_deleted': 'Prompt gelöscht',
                'prompt_save_error': 'Fehler beim Speichern',
                'prompt_not_found': 'Prompt nicht gefunden',
                'prompt_delete_error': 'Fehler beim Löschen',
                'close_button': 'Schließen',
                'select_button': 'Auswählen',
                'cancel_button': 'Abbrechen',
                'ocr_processing': 'Text aus Bild erkennen...',
                'ocr_success': 'Text erkannt!',
                'ocr_no_text': 'Kein Text gefunden',
                'ocr_error_message': 'Erkennungsfehler',
                'voice_recording': 'Aufnahme...',
                'voice_error_timeout': 'Zeitüberschreitung',
                'voice_error_unknown': 'Sprache nicht erkennbar',
                'voice_error_service': 'Dienstfehler',
                'voice_error_general': 'Erkennungsfehler',
                'code_label': 'Code',
                'code_copy': 'Code kopieren',
                'code_copied': 'Code kopiert',
                'image_select_title': 'Bild auswählen',
                'image_processed': 'Bild verarbeitet',
                'image_saved': 'Bild gespeichert',
                'system_prompt_instruction': 'Geben Sie einen System-Prompt für den aktuellen Chat ein.\nEr wird für alle folgenden Anfragen verwendet.'
            },
            'PT': {
                'prompt_input': 'Sua pergunta...',
                'prompt_input_field': 'Insira o prompt do sistema...',
                'loading_message': 'Pensando...',
                'dialog_title': 'Tem certeza de que deseja limpar este chat?',
                'dialog_text': 'Esta ação não pode ser desfeita',
                'confirm_clear_button': 'Sim',
                'cancel_clear_button': 'Cancelar',
                'new_chat_item': '+ Novo chat',
                'no_chats_item': 'Nenhum chat criado',
                'chats_dialog_title': 'Seus chats',
                'text_field': 'Digite um novo nome',
                'rename_dialog_title': 'Renomear chat',
                'cancel_rename_button': 'Cancelar',
                'confirm_rename_button': 'Salvar',
                'language_dialog': 'Escolher idioma',
                'prompt_dialog_title': 'Prompt do sistema',
                'save_prompt_button': 'Salvar',
                'delete_prompt_button': 'Excluir',
                'response_error': 'Erro ao obter resposta',
                'request_error': 'Erro na solicitação',
                'image_error': 'Erro ao gerar imagem',
                'voice_error': 'Erro na gravação de voz',
                'ocr_error': 'Erro no reconhecimento de texto',
                'prompt_saved': 'Prompt salvo',
                'prompt_deleted': 'Prompt excluído',
                'prompt_save_error': 'Erro ao salvar',
                'prompt_not_found': 'Prompt não encontrado',
                'prompt_delete_error': 'Erro ao excluir',
                'close_button': 'Fechar',
                'select_button': 'Selecionar',
                'cancel_button': 'Cancelar',
                'ocr_processing': 'Reconhecendo texto da imagem...',
                'ocr_success': 'Texto reconhecido!',
                'ocr_no_text': 'Nenhum texto encontrado',
                'ocr_error_message': 'Erro no reconhecimento',
                'voice_recording': 'Gravando...',
                'voice_error_timeout': 'Tempo esgotado',
                'voice_error_unknown': 'Não foi possível reconhecer',
                'voice_error_service': 'Erro no serviço',
                'voice_error_general': 'Erro no reconhecimento',
                'code_label': 'Código',
                'code_copy': 'Copiar código',
                'code_copied': 'Código copiado',
                'image_select_title': 'Selecionar imagem',
                'image_processed': 'Imagem processada',
                'image_saved': 'Imagem salva',
                'system_prompt_instruction': 'Insira um prompt do sistema para o chat atual.\nSerá usado para todas as consultas subsequentes.'
            }
        }

    def get_available_languages(self):
        '''Возвращает список доступных языков'''
        return self._available_languages

    def get_file_path(self):
        '''Получает путь к файлу имени языка'''
        if platform == 'android':
            return os.path.join(app_storage_path(), self.lang_file)
        else:
            return os.path.join(os.path.dirname(__file__), self.lang_file)

    def _ensure_lang_file(self):
        '''Создает файл с языком если его нет'''
        path = self.get_file_path()
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as file:
                file.write('RU')

    def add_language_to_file(self, lang: str):
        '''Сохраняет имя языка в файл'''
        self._ensure_lang_file()
        file_path = self.get_file_path()
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(lang)

    def get_saved_language(self):
        '''Получает сохраненный язык'''
        self._ensure_lang_file()
        file_path = self.get_file_path()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lang = file.read().strip()
                if lang in self._translations:
                    return lang
        except:
            pass
        return 'RU'

    def translate_interface(self, lang: str = None) -> dict:
        '''Возвращает словарь с переводами для указанного языка'''
        if lang is None:
            lang = self.get_saved_language()
        return self._translations.get(lang, self._translations['RU'])

    # language_manager.py - обновленный метод translate_prompts

    def translate_prompts(self, lang: str = None) -> dict:
        '''Возвращает словарь с переведенными системными промптами'''
        prompts = {
            'RU': [
                'Ты AI ассистент, по имени PonGPT, созданная, чтобы помогать пользователю. Ты находишься в приложении с чатом, где пользователь задает тебе вопросы.',
                'При ответах ты используешь разметку markdown. Вот как тебе стоит ее использовать: [b]Жирный текст[/b], [i]Курсив[/i], [u]Подчеркнутый[/u]. Ты не добавляешь эмодзи и любые другие символы, не входящие в наборы ASCII или кириллицы. Используй только буквы латиницы, кириллицы, цифры и стандартные знаки препинания. Если ты пишешь код на Python, оборачивай его в теги [code] и [/code]. Например: [code]print("Hello World!")[/code]',
                'Ты умеешь генерировать картинки. Если пользователь спросит, что ему нужно для этого сделать, скажи, чтобы он написал "Нарисуй {то, что ты хочешь нарисовать}"',
                'Если сообщение пользователя начинается с "The text at photo:" - это означает, что пользователь отсканировал изображение с текстом. Не удивляйся, если в тексте будет много ошибок, так как распознавание текста с изображений может работать не идеально. Отвечай на содержание распознанного текста как на обычный запрос, игнорируя возможные опечатки и ошибки распознавания.'
            ],
            'EN': [
                'You are an AI assistant named PonGPT, created to help the user. You are in a chat application where the user asks you questions.',
                'When responding, you use Markdown formatting. Here is how you should use it: [b]Bold text[/b], [i]Italic[/i], [u]Underlined[/u]. You do not add emojis or any other characters that are not part of ASCII or Cyrillic character sets. Use only Latin letters, Cyrillic letters, digits, and standard punctuation marks. If you write Python code, wrap it in [code] and [/code] tags. For example: [code]print("Hello World!")[/code]',
                'You can generate images. If a user asks what they need to do, tell them to write "Draw {what you want to draw}."',
                'If a user message starts with "The text at photo:" - this means the user has scanned an image with text. Do not be surprised if the text contains many errors, as text recognition from images may not work perfectly. Respond to the content of the recognized text as a normal query, ignoring possible typos and recognition errors.'
            ],
            'FR': [
                'Vous êtes un assistant IA nommé PonGPT, créé pour aider l\'utilisateur. Vous êtes dans une application de chat où l\'utilisateur vous pose des questions.',
                'Lorsque tu réponds, tu utilises le formatage Markdown. Voici comment tu dois l\'utiliser : [b]Gras[/b], [i]Italique[/i], [u]Souligné[/u]. Tu n\'ajoutes pas d\'émoticônes ou d\'autres caractères qui ne font pas partie des ensembles de caractères ASCII ou cyrillique. Utilise uniquement des lettres latines, des lettres cyrilliques, des chiffres et des signes de ponctuation standard. Si tu écris du code Python, encadre-le avec les balises [code] et [/code]. Par exemple : [code]print("Bonjour le monde !")[/code]',
                'Tu sais generer des images. Si un utilisateur demande ce qu\'il doit faire pour cela, dis-lui d\'ecrire « Dessine {ce qu\'il veut dessiner} ».',
                'Si un message utilisateur commence par "The text at photo:" - cela signifie que l\'utilisateur a scanné une image contenant du texte. Ne sois pas surpris si le texte contient de nombreuses erreurs, car la reconnaissance de texte à partir d\'images peut ne pas fonctionner parfaitement. Réponds au contenu du texte reconnu comme à une requête normale, en ignorant les éventuelles fautes de frappe et erreurs de reconnaissance.'
            ],
            'ZH': [
                'Ni shi yi ge ming wei PonGPT de AI zhu shou, zhi zai bang zhu yong hu. Ni zai yi ge liao tian ying yong cheng xu zhong, yong hu xiang ni ti wen.',
                'Dāng nǐ huídá shí, nǐ shǐyòng Markdown biāojì yǔfǎ. Zhèlǐ shì rúhé shǐyòng: [b]Jiātǐ wénzì[/b], [i]Xiétǐ[/i], [u]Xiàhuà xiàn[/u]. Nǐ bù tiānjiā biǎoqíng fúhào huò qítā bù shǔyú ASCII huò Xīlǐ\'ěr zìfú jí de zìfú. Shǐyòng zhǐ yīngwén zìmǔ, xīlǐ\'ěr zìmǔ, shùzì hé biāozhǔn biāodiǎn fúhào. Rúguǒ nǐ xiě Python dàimǎ, yòng [code] hé [/code] biāoqiān bāoguǒ tā. Lìrú: [code]print("Nǐ hǎo, shìjiè!")[/code]',
                'Nǐ huì shēngchéng túpian. Rúguǒ yònghù wèn tā xūyào zùo shénme cáinéng zùodào zhèyīdiǎn, gàosù tā ràng tā xiě "Nàishuǐ {nǐ xiǎng nàishuǐ de dōngxī}"',
                'Rúguǒ yònghù xiāoxi kāishǐ yú "The text at photo:" - zhè yìwèizhe yònghù yǐjīng sǎomiǎole bāohán wénzì de túxiàng. Bùyào jīngyà rúguǒ wénzì zhōng yǒu hěnduō cuòwù, yīnwèi túxiàng wénzì shìbié kěnéng wúfǎ wánměi yùnxíng. Duì shìbié chū de wénzì nèiróng jìnxíng huídá, hūlüè kěnéng de dǎcuò hé shìbié cuòwù.'
            ],
            'ES': [
                'Eres un asistente de IA llamado PonGPT, creado para ayudar al usuario. Estás en una aplicación de chat donde el usuario te hace preguntas.',
                'Cuando respondas, utilizas el formato Markdown. Así es como debes usarlo: [b]Negrita[/b], [i]Cursiva[/i], [u]Subrayado[/u]. No agregas emojis ni otros caracteres que no formen parte de los conjuntos de caracteres ASCII o cirílico. Utiliza solo letras latinas, letras cirílicas, dígitos y signos de puntuación estándar. Si escribes código en Python, enciérralo con las etiquetas [code] y [/code]. Por ejemplo: [code]print("¡Hola, mundo!")[/code]',
                'Puedes generar imágenes. Si un usuario pregunta qué debe hacer, dile que escriba "Dibuja {lo que quieras dibujar}".',
                'Si un mensaje de usuario comienza con "The text at photo:" - significa que el usuario ha escaneado una imagen con texto. No te sorprendas si el texto contiene muchos errores, ya que el reconocimiento de texto a partir de imágenes puede no funcionar perfectamente. Responde al contenido del texto reconocido como a una consulta normal, ignorando posibles errores tipográficos y de reconocimiento.'
            ],
            'DE': [
                'Du bist ein KI-Assistent namens PonGPT, der entwickelt wurde, um dem Benutzer zu helfen. Du befindest dich in einer Chat-Anwendung, in der der Benutzer dir Fragen stellt.',
                'Wenn du antwortest, verwendest du die Markdown-Formatierung. So solltest du sie verwenden: [b]Fetter Text[/b], [i]Kursiv[/i], [u]Unterstrichen[/u]. Du fügst keine Emojis oder andere Zeichen hinzu, die nicht zu den ASCII- oder kyrillischen Zeichensätzen gehören. Verwende nur lateinische Buchstaben, kyrillische Buchstaben, Ziffern und Standard-Interpunktionszeichen. Wenn du Python-Code schreibst, umschließe ihn mit den Tags [code] und [/code]. Zum Beispiel: [code]print("Hallo Welt!")[/code]',
                'Du kannst Bilder generieren. Wenn ein Nutzer fragt, was er dafur tun muss, sag ihm, er solle „Zeichne {das, was du zeichnen mochtest}“ schreiben.',
                'Wenn eine Benutzernachricht mit "The text at photo:" beginnt - bedeutet dies, dass der Benutzer ein Bild mit Text gescannt hat. Sei nicht überrascht, wenn der Text viele Fehler enthält, da die Texterkennung aus Bildern möglicherweise nicht perfekt funktioniert. Antworte auf den Inhalt des erkannten Textes wie auf eine normale Anfrage und ignoriere mögliche Tippfehler und Erkennungsfehler.'
            ],
            'PT': [
                'Você é um assistente de IA chamado PonGPT, criado para ajudar o usuário. Você está em um aplicativo de chat onde o usuário faz perguntas.',
                'Quando você responder, utilize a formatação Markdown. Aqui está como você deve usá-la: [b]Negrito[/b], [i]Itálico[/i], [u]Sublinhado[/u]. Você não adiciona emojis ou outros caracteres que não fazem parte dos conjuntos de caracteres ASCII ou cirílico. Use apenas letras latinas, letras cirílicas, dígitos e sinais de pontuação padrão. Se você escrever código em Python, envolva-o com as tags [code] e [/code]. Por exemplo: [code]print("Olá, mundo!")[/code]',
                'Voce pode gerar imagens. Se um usuário perguntar o que precisa fazer, diga para ele escrever "Desenhe {o que voce quer desenhar}".',
                'Se uma mensagem do usuário começar com "The text at photo:" - isso significa que o usuário escaneou uma imagem com texto. Não se surpreenda se o texto contiver muitos erros, pois o reconhecimento de texto a partir de imagens pode não funcionar perfeitamente. Responda ao conteúdo do texto reconhecido como a uma consulta normal, ignorando possíveis erros de digitação e de reconhecimento.'
            ]
        }
        return prompts.get(lang, prompts['RU'])
