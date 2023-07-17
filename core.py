from pprint import pprint
from datetime import datetime

import vk_api
from vk_api.exceptions import ApiError
from config import access_token


class VkTools:
    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)

    def get_profile_info(self, user_id):
        try:
            info, = self.api.method('users.get', {
                'user_id': user_id,
                'fields': 'city,bdate,sex,relation,home_town'
            })
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        result = {'name': info['first_name'] + ' ' + info['last_name'] if
                  'first_name' in info and 'last_name' in info else None,
                  'sex': info.get('sex'),
                  'city': info.get('city')['title'] if info.get('city') is not None else None,
                  'bdate': info.get('bdate')
                  }
        return result

    def search_users(self, params):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']

        current_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = current_year - user_year
        age_from = age - 5
        age_to = age + 5

        users = self.api.method('users.search', {
            'count': 10,
            'offset': 0,
            'age_from': age_from,
            'age_to': age_to,
            'sex': sex,
            'city': city,
            'status': 6,
            'is_closed': False
        })

        try:
            users = users['items']
        except KeyError:
            return []

        res = []
        for user in users:
            if not user['is_closed']:
                res.append({'id': user['id'], 'name': user['first_name'] + ' ' + user['last_name']})

        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get', {
            'user_id': user_id,
            'album_id': 'profile',
            'extended': 1
        })

        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []
        for photo in photos:
            res.append({
                'owner_id': photo['owner_id'],
                'id': photo['id'],
                'likes': photo['likes']['count'],
                'comments': photo['comments']['count']
            })

        res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)
        return res


if __name__ == '__main__':
    bot = VkTools(access_token)
    params = bot.get_profile_info(789657038)
    users = bot.search_users(params)
    print(bot.get_photos(users[2]['id']))