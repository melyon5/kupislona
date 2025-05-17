from flask import Flask, request, jsonify
import logging
import random
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

cities = {
    'москва': ['1540737/2894c590796fd3076441', '1533899/2f77c7cc982f0ac961d3', '1533899/ab5f38d5f3ed3b2ce296'],
    'нью-йорк': ['997614/f2b057aba5c1844bff83', '1540737/8ff7f9ad5123b333ba8c', '1652229/d9a58990b0f4abc31c67'],
    'париж': ['937455/79e2f262cbd06e2fa876', '1521359/8857301fbc989dc37a48', '1030494/a2f42a7fa2cbe832eaf0']
}

session_data = {}

def get_country(city):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13",
            "geocode": city,
            "format": "json"
        }
        data = requests.get(url, params).json()
        return data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['CountryName']
    except Exception as e:
        return e

@app.route('/', methods=['POST'])
def main():
    req = request.json
    logging.info('Request: %r', req)
    res = {
        'session': req['session'],
        'version': req['version'],
        'response': {'end_session': False}
    }
    if req['request']['original_utterance'].lower() == 'помощь':
        res['response']['text'] = 'Попробуй угадать город по фото, а затем его страну.'
    else:
        process_dialog(res, req)
        if 'buttons' not in res['response']:
            res['response']['buttons'] = []
        res['response']['buttons'].append({'title': 'Помощь', 'hide': True})
    logging.info('Response: %r', res)
    return jsonify(res)

def process_dialog(res, req):
    uid = req['session']['user_id']
    if req['session']['new']:
        session_data[uid] = {'first_name': None, 'game_started': False}
        res['response']['text'] = 'Привет! Как тебя зовут?'
        return

    if session_data[uid]['first_name'] is None:
        name = extract_name(req)
        if name is None:
            res['response']['text'] = 'Я не поняла имя. Повтори, пожалуйста.'
        else:
            session_data[uid]['first_name'] = name
            session_data[uid]['guessed'] = []
            res['response']['text'] = f'{name.title()}, рада знакомству! Угадай город на фото?'
            res['response']['buttons'] = [{'title': 'Да', 'hide': True}, {'title': 'Нет', 'hide': True}]
    else:
        if not session_data[uid]['game_started']:
            if 'да' in req['request']['nlu']['tokens']:
                if len(session_data[uid]['guessed']) == 3:
                    res['response']['text'] = 'Ты угадал все города!'
                    res['response']['end_session'] = True
                else:
                    session_data[uid]['game_started'] = True
                    session_data[uid]['step'] = 1
                    run_game(res, req)
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Хорошо, тогда в другой раз.'
                res['response']['end_session'] = True
            else:
                res['response']['text'] = 'Ты хочешь играть?'
                res['response']['buttons'] = [{'title': 'Да', 'hide': True}, {'title': 'Нет', 'hide': True}]
        else:
            run_game(res, req)

def run_game(res, req):
    uid = req['session']['user_id']
    step = session_data[uid]['step']

    if step == 1:
        city = random.choice(list(cities))
        while city in session_data[uid]['guessed']:
            city = random.choice(list(cities))
        session_data[uid]['city'] = city
        res['response']['card'] = {
            'type': 'BigImage',
            'title': 'Узнай город!',
            'image_id': cities[city][step - 1]
        }
        res['response']['text'] = 'Поехали!'

    elif step == -1:
        city = session_data[uid]['city']
        country = get_country(city)
        if country.lower() in req['request']['original_utterance'].lower():
            res['response']['text'] = 'Верно! Хочешь попробовать ещё?'
            res['response']['buttons'] = [{
                'title': 'Показать на карте',
                'url': f'https://yandex.ru/maps/?mode=search&text={city}',
                'hide': True
            }]
            session_data[uid]['guessed'].append(city)
            session_data[uid]['game_started'] = False
        else:
            res['response']['text'] = 'Не угадал. Попробуй ещё.'
        return

    else:
        city = session_data[uid]['city']
        if extract_city(req) == city:
            res['response']['text'] = 'Точно! А теперь угадай страну.'
            res['response']['buttons'] = [{
                'title': 'Показать на карте',
                'url': f'https://yandex.ru/maps/?mode=search&text={city}',
                'hide': True
            }]
            session_data[uid]['step'] = -1
            return
        else:
            if step == 4:
                res['response']['text'] = f'Это был город {city.title()}. Попробуем другой?'
                session_data[uid]['guessed'].append(city)
                session_data[uid]['game_started'] = False
                return
            else:
                res['response']['card'] = {
                    'type': 'BigImage',
                    'title': 'Попробуй ещё раз',
                    'image_id': cities[city][step - 1]
                }
                res['response']['text'] = 'Не тот город.'
    session_data[uid]['step'] += 1

def extract_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city')

def extract_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
