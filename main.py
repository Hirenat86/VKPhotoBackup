import os
import requests
import json
from dotenv import load_dotenv

dotenv_path = 'config.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

VK_TOKEN = os.getenv('VK_TOKEN')
YA_TOKEN = os.getenv('YA_TOKEN')

class VKPhotoBackup:
    def __init__(self, access_token, version='5.199'):
        self.access_token = access_token
        self.version = version
        self.base_url = 'https://api.vk.com/method/'
        self.params = {
            'access_token': access_token,
            'v': self.version,
        }

    def get_user_info(self, user_id):
        url = f'{self.base_url}users.get'
        params = {
            **self.params,
            'user_ids': user_id
        }
        response = requests.get(url, params=params)
        return response.json()

    def get_photo_info(self, user_id, count = 5):
        url = f'{self.base_url}photos.get'
        params = {
            **self.params,
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'count': count
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error fetching photos: {response.status_code}")
            return None
        return response.json()



class YD_dowloadeer:

    def __init__(self, YD_token):
        self.headers = {'Authorization': f'OAuth {YD_token}'}
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/resources'

    def create_folder(self, folder_name):
        response = requests.put(self.base_url, headers=self.headers, params = {"path": folder_name})
        if response.status_code == 201:
            print(f'Папка "{folder_name}" успешно создана.')
        elif response.status_code == 409:
            print(f'Папка с именем "{folder_name}" уже существует.')
        else:
            print(f'Не удалось создать папку "{folder_name}". Ошибка: {response.status_code}')
            print(f'Ответ API: {response.json()}')
        return response.status_code

    def upload_url(self, photo_url, file_name):
        upload_url = f'{self.base_url}/upload'
        params = {
            'path': f'/VKPhotoBackup/{file_name}',
            'url': photo_url
        }
        response_upload = requests.post(upload_url, headers=self.headers, params = params)
        return response_upload.status_code


if __name__ == '__main__':
    vk_connector = VKPhotoBackup(VK_TOKEN)
    photo_info = vk_connector.get_photo_info(3223752)
    yd_connector = YD_dowloadeer(YA_TOKEN)
    results = []
    for item in photo_info['response']['items']:
        file_name = f'{item['likes']['count']}.jpg'
        photo_url = item['sizes'][-1]['url']
        if yd_connector.upload_url(photo_url, file_name) == 202:
            print(f'Файл "{file_name}" успешно загружен.')
        else:
            print(f'Ошибка загрузки файла "{file_name}"')

        results.append({'file_name': file_name, 'size': item['sizes'][-1]['type']})

    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)
    print("Results saved to results.json")





