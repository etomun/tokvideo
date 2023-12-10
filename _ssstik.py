import os
import shutil
from os import makedirs
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

import requests

__cookies = {
    '_ga': 'GA1.1.179538163.1700803879',
    '__gads': 'ID=6e408608e499df57:T=1700803879:RT=1701417226:S=ALNI_MaGe9bfTzCkJx50hc114A_ASq8QFA',
    '_ga_ZSF3D6YSLC': 'GS1.1.1701417225.6.1.1701417318.0.0.0',
}

__headers = {
    'authority': 'ssstik.io',
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7,id;q=0.6',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'hx-current-url': 'https://ssstik.io/en',
    'hx-request': 'true',
    'hx-target': 'target',
    'hx-trigger': '_gcaptcha_pt',
    'origin': 'https://ssstik.io',
    'referer': 'https://ssstik.io/en',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}


def __post_link(tiktok_url: str):
    params = {'url': 'dl', }
    data = {'id': tiktok_url, 'locale': 'en', 'tt': 'ZUY2YXM1', }
    r = requests.post('https://ssstik.io/abc', params=params, cookies=__cookies, headers=__headers, data=data)
    print(f'{r}: Generated Tiktok link by requests {tiktok_url}')


def get_old_video(video_url: str, shop_url: str) -> str:
    video_id = PurePosixPath(unquote(urlparse(video_url).path)).parts[-1:][0]
    shop_path, product_path = PurePosixPath(unquote(urlparse(shop_url).path)).parts[-2:]
    file = f'data/videos/{shop_path}/{product_path}/{video_id}'
    if os.path.exists(file):
        size = round(os.path.getsize(file) / (1024 * 1024))
        print(f'Found old video: {file} - {size} MB')
        return file
    else:
        return ""


def download_shop_ee_video(video_url: str, shop_url: str) -> str:
    video_id = PurePosixPath(unquote(urlparse(video_url).path)).parts[-1:][0]
    shop_path, product_path = PurePosixPath(unquote(urlparse(shop_url).path)).parts[-2:]
    file_dir = f'data/videos/{shop_path}/{product_path}'
    file = f'{file_dir}/{video_id}'
    makedirs(file_dir, exist_ok=True)

    with requests.get(video_url, stream=True) as r:
        with open(file, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f, length=8 * 1024)
    size = os.path.getsize(file) / (1024 * 1024)
    print(f'Shop*ee video downloaded {file} - {size}MB')
    return file


def download_tiktok_video(tiktok_url: str, shop_url: str) -> str:
    __post_link(tiktok_url)
    video_id = PurePosixPath(unquote(urlparse(tiktok_url).path)).parts[-1:][0]
    shop_path, product_path = PurePosixPath(unquote(urlparse(shop_url).path)).parts[-2:]
    url = f'https://tikcdn.io/ssstik/{video_id}'
    file_dir = f'data/videos/{shop_path}/{product_path}'
    file = f'{file_dir}/{video_id}.mp4'

    if os.path.exists(file) and os.path.getsize(file) > 0:
        size = round(os.path.getsize(file) / (1024 * 1024))
        print(f'Tiktok video already exists {file} - {size} MB')
        return file
    else:
        makedirs(file_dir, exist_ok=True)
        with requests.get(url, cookies=__cookies, headers=__headers, stream=True) as r:
            with open(file, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f, length=8 * 1024)
        size = round(os.path.getsize(file) / (1024 * 1024))
        print(f'Tiktok video downloaded {file} - {size} MB')
        return file


def download_tiktok(tiktok_url: str) -> str:
    __post_link(tiktok_url)
    video_id = PurePosixPath(unquote(urlparse(tiktok_url).path)).parts[-1:][0]
    url = f'https://tikcdn.io/ssstik/{video_id}'
    file_dir = 'data/videos/tiktok'
    tiktok_file = f'{file_dir}/{video_id}.mp4'

    file_existed = os.path.exists(tiktok_file)
    if file_existed and os.path.getsize(tiktok_file) > 0:
        size = round(os.path.getsize(tiktok_file) / (1024 * 1024))
        print(f'Tiktok video already exists {tiktok_file} - {size} MB')
        return tiktok_file
    else:
        makedirs(file_dir, exist_ok=True)
        with requests.get(url, cookies=__cookies, headers=__headers, stream=True) as r:
            with open(tiktok_file, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f, length=8 * 1024)
        size = round(os.path.getsize(tiktok_file) / (1024 * 1024))
        print(f'Tiktok video downloaded {tiktok_file} - {size} MB')
        return tiktok_file
