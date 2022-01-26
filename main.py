import json
import requests
import os
from urllib.request import urlretrieve
import sys
import yadisk
from tqdm import tqdm


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self):
        with open('token1.txt', 'r') as file_object:
            token = file_object.read().strip()
        self.params = {
            'access_token': token,
            'v': '5.131',
        }

    def get_photos(self, user_id=None):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'count': 5,
            'user_id': user_id,
            'album_id': 'profile',
            'photo_sizes': 1,
            'extended': 1
        }
        res = requests.get(photos_url, params={**self.params, **photos_params}).json()
        # pprint(res)
        return res

    def max_photo_size(self, user_id=None):
        all_photos = self.get_photos(user_id)
        url_list = []
        i = int()
        for photo in all_photos['response']['items']:
            h_w = int()
            url = str()
            type = str()
            likes = all_photos['response']['items'][i]['likes']['count']
            for size in photo['sizes']:
                if size['height'] * size['width'] > h_w:
                    h_w = size['height'] * size['width']
                    url = size['url']
                    type = size['type']
            url_list.append([url, likes, type])
            i += 1
        # pprint(url_list)
        return url_list

    def download_photos(self, user_id=None):
        url_list = self.max_photo_size(user_id)
        newpath = os.path.join(sys.path[0], user_id)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        for photo_url in url_list:
            img_name = str(photo_url[1])
            urlretrieve(photo_url[0], newpath + '/' + str(img_name) + '.jpg')

    def save_photo_information(self, user_id=None):
        all_photos = self.max_photo_size(user_id)
        inf_list = []
        i = int()
        newpath = os.path.join(sys.path[0], user_id)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        for inf in all_photos:
            photo_information = {'file_name': all_photos[i][1], 'size': all_photos[i][2]}
            inf_list.append(photo_information)
            i += 1
        # pprint(inf_list)
        with open(newpath + '/photos_information.json', mode='w', encoding='utf-8') as file:
            json.dump(inf_list, file, indent=4)


class Uploader:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def get_upload_link(self, user_id):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": user_id, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, user_id):
        ya = yadisk.YaDisk(token=self.token)
        ya.mkdir(user_id)
        path = os.getcwd()
        dir_name = os.path.join(path, user_id)
        for file in os.listdir(dir_name):
            href = self.get_upload_link(f'{user_id}/{file}').get('href', '')
            file_path = os.path.join(dir_name, file)
            requests.put(href, open(file_path, mode='rb'))


def main(user_id=None, token=None):
    vk_client = VkUser()
    ya_vk_client = Uploader(token)
    pbar = tqdm(total=100)
    for i in range(100):
        vk_client.download_photos(user_id)
        pbar.update(float(100/3))
        vk_client.save_photo_information(user_id)
        pbar.update(float(100/3))
        ya_vk_client.upload_file_to_disk(user_id)
        pbar.update(float(100/3))
        break
    pbar.close()

if __name__ == '__main__':
    main('', '')
