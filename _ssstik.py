import shutil
from os import makedirs
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

import requests
from playwright.sync_api import sync_playwright

__cookies = {
    '_ga': 'GA1.1.179538163.1700803879',
    '__gads': 'ID=6e408608e499df57:T=1700803879:RT=1700833720:S=ALNI_MaGe9bfTzCkJx50hc114A_ASq8QFA',
    '_ga_ZSF3D6YSLC': 'GS1.1.1700833720.2.0.1700833865.0.0.0',
}

__headers = {
    'authority': 'ssstik.io',
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7',
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


def __ssstik_requests(tiktok_url: str):
    params = {'url': 'dl', }
    data = {'id': tiktok_url, 'locale': 'en', 'tt': 'cjhDVEdl', }
    r = requests.post('https://ssstik.io/abc', params=params, cookies=__cookies, headers=__headers, data=data)
    print(f'submit by requests: {tiktok_url}\n{r}')


def __ssstik_pw(tiktok_url: str):
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context()
        p = context.new_page()
        p.goto("https://ssstik.io/en")
        p.fill('input#main_page_text', tiktok_url)
        p.click('button#submit')
        print(f'submit by playwright: {tiktok_url}')
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
        print(f'Response: {r.raise_for_status()}')
        with open(file, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f, length=8 * 1024)
    return file


def download_tiktok_video(tiktok_url: str, shop_url: str) -> str:
    __ssstik_requests(tiktok_url)
    video_id = PurePosixPath(unquote(urlparse(tiktok_url).path)).parts[-1:][0]
    shop_path, product_path = PurePosixPath(unquote(urlparse(shop_url).path)).parts[-2:]
    url = f'https://tikcdn.io/ssstik/{video_id}'
    file_dir = f'data/videos/{shop_path}/{product_path}'
    file = f'{file_dir}/{video_id}.mp4'
    makedirs(file_dir, exist_ok=True)

    with requests.get(url, cookies=__cookies, headers=__headers, stream=True) as r:
        print(f'Response: {r.raise_for_status()}')
        with open(file, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f, length=8 * 1024)
    return file

# if __name__ == '__main__':
#     download_tiktok_video('https://www.tiktok.com/@dapuristrii.aw/video/7279286245308501253',
#                           'https://shopee.co.id/product/307192440/12350902437')
#
#     # download_tiktok_shop_ee('https://down-cvs-sg.vod.susercontent.com/c3/98934353/105/A3oxOF3KAEhOGXwKERABACY.mp4',
#     #                         'https://shopee.co.id/product/40847197/15576892572')
