from deep_translator import GoogleTranslator

def translate_word(word, target_language='en'):
    try:
        translation = GoogleTranslator(source='auto', target=target_language).translate(word)
        return translation
    except Exception as e:
        print(f"Не удалось перевести слово '{word}': {e}")
        return None
