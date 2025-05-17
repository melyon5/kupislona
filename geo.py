import requests
from math import sin, cos, sqrt, atan2, radians


import requests

def get_coordinates(city):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            'geocode': city.title(),  # Приводим к нормальному виду
            'format': 'json',
            'apikey': "40d1649f-0493-4b70-98ba-98533de7710b"
        }
        response = requests.get(url, params)
        data = response.json()

        features = data['response']['GeoObjectCollection']['featureMember']
        if not features:
            print(f"[ОШИБКА] Город не найден: {city}")
            return None

        point_str = features[0]['GeoObject']['Point']['pos']
        return [float(x) for x in point_str.split(' ')]

    except Exception as e:
        print(f"[ОШИБКА] Ошибка в get_coordinates('{city}'): {e}")
        return None

def get_country(city):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            'geocode': city,
            'format': 'json',
            'apikey': "6bf2895d-8652-402b-a66b-98ce0ace342c"
        }
        response = requests.get(url, params)
        data = response.json()

        features = data['response']['GeoObjectCollection']['featureMember']
        if not features:
            return "Не удалось определить страну"

        return features[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['CountryName']

    except Exception as e:
        print(f'Ошибка в get_country для города {city}: {e}')
        return "Ошибка получения страны"


def get_distance(p1, p2):
    if not p1 or not p2:
        return 0
    R = 6373.0
    lon1, lat1 = radians(p1[0]), radians(p1[1])
    lon2, lat2 = radians(p2[0]), radians(p2[1])
    dlon, dlat = lon2 - lon1, lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
