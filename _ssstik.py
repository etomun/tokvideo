import os
import shutil
from os import makedirs
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

import requests
from playwright.sync_api import sync_playwright

__cookies = {}

__headers = {}


def __ssstik_requests(tiktok_url: str):
    params = {'url': 'dl', }
    data = {'id': tiktok_url, 'locale': 'en', 'tt': '', }
    r = requests.post('https://ssstik.io/abc', params=params, cookies=__cookies, headers=__headers, data=data)
    print(f'{r}: Generated Tiktok link by requests {tiktok_url}')


def __ssstik_pw(tiktok_url: str):
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context()
        p = context.new_page()
        p.goto("https://ssstik.io/en")
        p.fill('input#main_page_text', tiktok_url)
        p.click('button#submit')
        print(f'Generated Tiktok link by requests: {tiktok_url}')
        # Continue Download Here
        # p.get_by_role("link", name="Without watermark").click()
        # with p.expect_download() as download_info:
        #     p.frame_locator("iframe[name=\"aswift_2\"]").get_by_label("Close ad").click()
        # downloaded_file = download_info.value
        # p.get_by_label("Close this dialog window").click()
        # downloaded_file.save_as(f'data/videos/{file_name}')
        context.close()
        browser.close()


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
    __ssstik_requests(tiktok_url)
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


if __name__ == '__main__':
    download_tiktok_video('https://www.tiktok.com/@khikmamakfiro/video/7265248373656096006',
                          'https://shopee.co.id/product/378273492/4996092496')
#
#     # download_tiktok_shop_ee('https://down-cvs-sg.vod.susercontent.com/c3/98934353/105/A3oxOF3KAEhOGXwKERABACY.mp4',
#     #                         'https://shopee.co.id/product/40847197/15576892572')
