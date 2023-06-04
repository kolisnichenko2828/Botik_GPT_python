from easygoogletranslate import EasyGoogleTranslate # для google translate

class Translate:
    async def translateToEn(self, text):
        try:
            translator = EasyGoogleTranslate(
                source_language='ru',
                target_language='en',
                timeout=10
            )
            result = translator.translate(text)
            return result
        except Exception as e:
            print(f'Error while translateToEn: {e}')

    async def translateToRu(self, text):
        try:
            translator = EasyGoogleTranslate(
                source_language='en',
                target_language='ru',
                timeout=10
            )
            result = translator.translate(text)
            return result
        except Exception as e:
            print(f'Error while translateToRu: {e}')

tr = Translate()