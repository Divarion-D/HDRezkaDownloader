import sys
import os
import requests
from tqdm import tqdm

HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/103.0.0.0 Safari/537.36 '
        }

API_URL = "http://127.0.1.1:8000/"

class Error(Exception):
    """Base class for other exceptions"""
    pass


class IncorrectEpisodeNumberException(Error):
    """Raised when incorrect episode number was in input"""
    pass


class EpisodeNumberIsOutOfRange(Error):
    """Raised when episode number is out of range of available episodes"""
    pass


class Download:
    def __init__(self):
        search_title = input("Введите название: ")

        search_request = requests.get(API_URL + f"content/search/?query={search_title}&page=1").json()
        for i in range(len(search_request)):
            print(f"{i} - {search_request[i]['title']}")
        series_id = int(input("Введите номер: "))
        self.url = search_request[series_id]["mirrorLessUrl"]
        self.title = search_request[series_id]["title"]

        detail_info_request = requests.get(API_URL + f"content/details/?url={self.url}").json()

        for i in range(len(detail_info_request["translations_id"])):
            print(f"{i} - {detail_info_request['translations_id'][i]['name']}")
        translation_id = int(input("Введите номер: "))
        translation_id = detail_info_request["translations_id"][translation_id]["id"]
        
        print ("1: Скачать сезон")
        print ("2: Скачать серию")
        print ("3: Скачать фильм")
        var_download = input("Выберите действие: ")
        var_download = "1"
        if var_download == "1":
            season_id = input("Введите номер сезона: ")
            self.Download_Season(season_id, translation_id)

    
    def Download_Season(self, season_id, translation_id):
        # get series list
        series_list = requests.get(API_URL + f"content/tv_series/seasons/?url={self.url}&translation_id={translation_id}").json()
        for i in range(1, len(series_list["episodes"][str(season_id)])+1):
            episode_source = requests.get(API_URL + f"content/tv_series/videos/?url={self.url}&translation_id={translation_id}&season_id={season_id}&episode_id={i}").json()
            file_name = f"{self.title} - {season_id}s{i}e.mp4"

            download_data = {
                'stream_url': episode_source['360p'],
                'file_name': file_name,
                'title': self.title
            }

            self.__download(download_data)


    @staticmethod
    def __download(download_data):
        if download_data['stream_url']:

            fullpath = os.path.join(os.path.curdir, 'temp', download_data["title"], download_data['file_name'])
            # remove symbols from fullpath
            fullpath = fullpath.replace(":", "")

            if not os.path.exists(os.path.dirname(fullpath)):
                os.makedirs(os.path.dirname(fullpath))

            with requests.get(url=download_data['stream_url'], stream=True, headers=HEADERS) as r, open(fullpath, "wb") as f, tqdm(
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    total=int(r.headers.get('content-length', 0)),
                    file=sys.stdout,
                    desc=download_data['file_name']
            ) as progress:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        datasize = f.write(chunk)
                        progress.update(datasize)


if __name__ == "__main__":
    Download()