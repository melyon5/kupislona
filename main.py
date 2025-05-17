from flask import Flask, request
import logging
import json
import os
from geo import get_country, get_distance, get_coordinates

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

    # Защита от ошибки: если текст не задан, пишем заглушку
    if 'text' not in response['response'] or not response['response']['text']:
        response['response']['text'] = 'Произошла ошибка. Попробуй ещё раз.'

    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = (
            'Привет! Я могу сказать, в какой стране находится город, '
            'или рассчитать расстояние между двумя городами.'
        )
        return

    cities = get_cities(req)
    logging.info(f'Обнаружены города: {cities}')

    if len(cities) == 0:
        res['response']['text'] = 'Ты не написал название ни одного города.'

    elif len(cities) == 1:
        country = get_country(cities[0])
        res['response']['text'] = f'Этот город в стране — {country}'

    elif len(cities) == 2:
        p1 = get_coordinates(cities[0])
        p2 = get_coordinates(cities[1])

        if p1 and p2:
            distance = get_distance(p1, p2)
            res['response']['text'] = f'Расстояние между этими городами: {round(distance)} км.'
        else:
            res['response']['text'] = 'Не удалось определить координаты одного из городов.'
            if not p1:
                logging.error(f'Не найдены координаты для города: {cities[0]}')
            if not p2:
                logging.error(f'Не найдены координаты для города: {cities[1]}')

    else:
        res['response']['text'] = 'Слишком много городов. Назови один или два города.'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value']:
                cities.append(entity['value']['city'])
    return cities


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # для Render
    app.run(host="0.0.0.0", port=port)
