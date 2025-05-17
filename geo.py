from math import sin, cos, sqrt, atan2, radians
import requests


def get_geo_info(city_name, type_info):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            'geocode': city_name.title(),
            'format': 'json',
            'apikey': "6bf2895d-8652-402b-a66b-98ce0ace342c"
        }

        response = requests.get(url, params)
        data = response.json()

        features = data['response']['GeoObjectCollection']['featureMember']
        if not features:
            print(f"[ОШИБКА] Город не найден: {city_name}")
            return None

        geo_object = features[0]['GeoObject']

        if type_info == 'coordinates':
            point_str = geo_object['Point']['pos']
            return [float(x) for x in point_str.split(' ')]

        elif type_info == 'country':
            return geo_object['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['CountryName']

        else:
            print(f"[ОШИБКА] Недопустимое значение type_info: {type_info}")
            return None

    except Exception as e:
        print(f"[ОШИБКА] Ошибка в get_geo_info('{city_name}', '{type_info}'): {e}")
        return None


def get_distance(p1, p2):
    if not p1 or not p2:
        return 0
    R = 6373.0
    lon1, lat1 = radians(p1[0]), radians(p1[1])
    lon2, lat2 = radians(p2[0]), radians(p2[1])
    dlon, dlat = lon2 - lon1, lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
