from flask import Flask, request
import logging
import json
import os
from translator import translate_word

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


@app.route('/', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)

    if 'text' not in response['response'] or not response['response']['text']:
        response['response']['text'] = 'Я не поняла, какое слово нужно перевести.'

    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    utterance = req['request']['original_utterance'].lower()

    if req['session']['new']:
        res['response']['text'] = 'Привет! Скажи, какое слово нужно перевести. Например: "переведи слово дом".'
        return

    word = extract_word(utterance)

    if word:
        translation = translate_word(word)
        if translation:
            res['response']['text'] = translation
        else:
            res['response']['text'] = 'Не удалось перевести это слово.'
    else:
        res['response']['text'] = 'Скажи, что нужно перевести. Например: "переведи слово школа".'


def extract_word(text):
    triggers = ['переведи слово ', 'переведите слово ']
    for trig in triggers:
        if trig in text:
            return text.split(trig)[-1].strip()
    return None


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
