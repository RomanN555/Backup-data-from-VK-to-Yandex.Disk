import requests
from pprint import pprint
import json
from dotenv import load_dotenv
import os
from tqdm import tqdm
import time
load_dotenv()
vk_access_token = os.getenv('VK_ACCESS_TOKEN')
yandex_oauth_token = os.getenv('YANDEX_OAUTH_TOKEN')

class VK:
    def __init__(self, access_token, version='5.131'):
        self.params = {'access_token': access_token, 'v': version}
        self.base_url = 'https://api.vk.com/method/'

    def get_photos(self, user_id, count=5):
        url = f'{self.base_url}photos.get'
        params = {
            'owner_id': user_id,
            'count': count,
            'album_id': 'profile',
            'extended': 1
        }
        params.update(self.params)
        response = requests.get(url, params=params)
        return response.json()

    def get_status(self, user_id):
        url = f'{self.base_url}status.get'
        params = {'owner_id': user_id}
        params.update(self.params)
        response = requests.get(url, params=params)
        return response.json()
    
    def users_info(self, user_id):
        url = f'{self.base_url}users.get'
        params = {'user_ids': user_id}
        params.update(self.params)
        response = requests.get(url, params=params)
        return response.json()
    
    def get_top_photos(self, user_id, count=5):
        response = self.get_photos(user_id, count=5)
        photos = response['response']['items']
        photo_data = []
        print("Обработываем фотографии...")
        for photo in tqdm(photos, desc="обработка фото"):
            sizes = photo['sizes']
            max_size = None
            for size in sizes:
                if max_size is None or size['width'] * size['height'] > max_size['width'] * max_size['height']:
                    max_size = size
            photo_data.append({
                'url': max_size['url'],
                'width': max_size['width'],
                'height': max_size['height'],
                'area': max_size['width'] * max_size['height'],
                'likes': photo['likes']['count'],
                'date': photo['date'],
            })

        sorted_photos = self.sorted_photo(photo_data, count=5)
        return sorted_photos
            
    def photo_get_area(self,photo):
        return photo['area']   
    
    def sorted_photo(self, photo_data, count=5):  
        return sorted(photo_data, key=self.photo_get_area,reverse=True)[:count]

class Yandex_disk:
    def __init__(self, OAuth_token):
        self.OAuth_token = OAuth_token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/'
        
    def Yandex_to_disk(self, public_url, name,save_folder='disk:/'):
        url = self.base_url + 'public/resources/save-to-disk'
        params =  {
            'public_key': public_url,
            'name': name,
            'save_path': save_folder
        }
        
        headers = {
        'Authorization': f'OAuth {self.OAuth_token}'
        }
        response = requests.post(url, params=params, headers=headers)
        return response

def save_photos_to_json(photo_data, filename='photos.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(photo_data, f, indent=4)

def save_result_json(result_list, filename='result.json'):
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(result_list, f, indent=4)

result_list = []
user_id = '345046789'
vk = VK(vk_access_token)
top_photki = (vk.get_top_photos(user_id, count=5))
for photo in tqdm(top_photki,desc="Загрузка фото на диск" ):
    photo_url = photo['url']  
    photo_name = f"{photo['likes']}_likes_photo.jpg"  

    yd = Yandex_disk(yandex_oauth_token)
    response = yd.Yandex_to_disk(public_url=photo_url, name=photo_name)
    result_list.append({
        "file_name": photo_name,
        "size": "z"
    })
    
top_photki = vk.get_top_photos(user_id, count=5)
save_photos_to_json(top_photki, 'photos.json')
save_result_json(result_list)