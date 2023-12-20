import argparse
import json
import subprocess
import time
from os import makedirs
from pathlib import PurePosixPath
from subprocess import PIPE
from urllib.parse import unquote, urlparse

import requests
from playwright.sync_api import sync_playwright, expect


def set_fav_product(usr: str, product_link: str, is_fav: bool) -> bool:
    print(f'{usr} try to set favorite:{is_fav} to {product_link}')
    shop_id, product_id = PurePosixPath(unquote(urlparse(product_link).path)).parts[-2:]
    endpoint = 'like_items' if is_fav else 'unlike_items'
    cookies_dic = _get_cookies(usr)
    cookies_str = '; '.join([f'{key}={value}' for key, value in cookies_dic.items()])
    cookies = f'__LOCALE__null=ID; {cookies_str}'
    curl_command = [
        'curl',
        '-X', 'POST',
        f'https://shopee.co.id/api/v4/pages/{endpoint}',
        '-H', 'authority: shopee.co.id',
        '-H', 'accept: application/json',
        '-H', 'accept-language: en-US,en;q=0.9',
        '-H', 'content-type: application/json',

        # '-H', 'if-none-match-: 55b03-ea8c9f1ba75cb000a410ab50e9378bcc',
        '-H', 'origin: https://shopee.co.id',
        '-H', 'priority: u=1, i',
        '-H', 'referer: https://shopee.co.id',
        '-H', 'sec-ch-ua: "Chromium";v="121", "Not A(Brand";v="99"',
        '-H', 'sec-ch-ua-mobile: ?0',
        '-H', 'sec-ch-ua-platform: "macOS"',
        '-H', 'sec-fetch-dest: empty',
        '-H', 'sec-fetch-mode: cors',
        '-H', 'sec-fetch-site: same-origin',
        '-H',
        'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        '-H', 'x-api-source: pc',
        '-H', 'x-csrftoken: bZ4aC5e1qrOzU0NJIHKgP7Xmpfm3Egg8',
        '-H', 'x-requested-with: XMLHttpRequest',
        '-H', 'x-sap-ri: 09677065df438387b6b73a320101e8c75ff0419416989f59ba49',
        '-H',
        'x-sap-sec: OMHEgbRcxmzRbmzRacz6bmARaczRbmARbmzNbmzRnmbRbl5cbmljbFzRamzRbaIqOop6bmzRSmjRba5dbmyi5KFvPwXXxfxjim42dp594OsqJXY3EpDh0MBOSPj0T4y2epIH12xgwInansk4n/iEawi4OWjOY7/eubOL5aXDhd+EiANGrXDYD4gnImx54wyC/VsxuuSplGMxq4uI4itrm/o1GQf+y31658KWTRPTZcUOPIwsPEWD4xjrPgWeXsyvKLmq+9XzrxyG5npA/XCGNx8kpLFdj1ts6B6h3bum4qVfqPVPY2+MxQTwtNRWISxXN5udNQX02ct2imae2rQSPXQ/IkZeAPHj5XKT0SMrK7usab5JSEAJyrMmv/EVQYsKAIfYs9pXIA0shHPRih/wTuDgWC3QjfpCBFHHwoiFcaazJJ+0ceCHmRNSduqu+VvYkZyaRnHYijlWx+4hYQIS6pxGO4yUZlHCu9c6qSVvcMwOlNJMkLb+oNmhHH3XzmZzwz5BqPTHwkWzeVgi/8vJGh6dJtKuU4BX/O/6UVebZnQq3ZVM6iXwnvTuYrC+FU+VL1YTyrYh2fHFrnMBcBWPwued7wjMmCW6zsruMZIghRudfhLKuqEJcYb4smV+DJra404gf0DKY8Pl49kBBeCXojAXgoX/EDOCV7N6bmzRTdzFA4uDgyVRbmzRLYsnOJRRbmzpbmzRYmzRbZOeHQHkrND2Yj5cEV6f1zRghtF+ZmzRbyA8iNXDidYmbmzRbGInOop6bmzRCmzRblARbmm4jxO6PekxjNxuli0SuZCj1yTaxmRRbmyjTjjVjyjFTmzRbmz6bm5RZmzNbmRRbmz6bmzRCmzRblARbmlv5dmMfl2+HmyI+tR/oSvbvgPorJRRbmz9A4bATNTlimzRbml=',
        '-H', 'x-shopee-language: id',
        '-d', f'{{"shop_item_ids":[{{"shop_id":{shop_id},"item_id":{product_id}}}]}}',
        '-b', cookies,
        '--compressed'
    ]

    try:
        process = subprocess.Popen(curl_command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        # Check if successful (exit code 0)
        if process.returncode == 0:
            response_json = json.loads(stdout.decode('utf-8'))
            print(response_json)
            return response_json['error'] == 0

        else:
            print(f"Error running cURL command. stderr: {stderr.decode('utf-8')}")
            return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def get_limits(total_limit):
    limits = []
    while total_limit >= 50:
        limits.append(50)
        total_limit -= 50
    if total_limit > 0:
        limits.append(total_limit)
    return limits if len(limits) > 0 else [0]


def get_product_offers(usr: str, keyword: str, limit: int) -> list:
    url = f"https://affiliate.shopee.co.id/api/v3/offer/product/list"
    products = []
    for i, page_limit in enumerate(get_limits(limit)):
        page_offset = i * 50

        # sort by commission (5)
        # sort by selling (2)
        # filter by Extra Commission
        querystring = {"keyword": keyword, "list_type": 0, "match_type": 1, "sort_type": 2, "page_offset": page_offset,
                       "page_limit": page_limit, "client_type": 1, "filter_types": 2, "filter_shop_types": 1}
        response = requests.request("GET", url,
                                    cookies=_get_cookies(usr),
                                    headers=_affiliate_headers(usr),
                                    params=querystring).json()
        try:
            datas = response['data']['list']
            print(f'Response {keyword} Page {i + 1}: {len(datas)}')
            products += datas
        except Exception as e:
            print(f'Error {keyword} Page {i + 1}: {e}')
            print(response)
            break

    print(f'Total Products: {len(products)}\n')
    if len(products) <= 0:
        print('Get no offer\n')
    return products


def get_related_products(usr: str, product_link: str) -> str:
    shop_id, product_id = PurePosixPath(unquote(urlparse(product_link).path)).parts[-2:]
    cookies_dic = _get_cookies(usr)
    cookies = '; '.join([f'{key}={value}' for key, value in cookies_dic.items()])
    url = f'https://shopee.co.id/api/v4/pdp/hot_sales/get?item_id={product_id}&limit=8&offset=0&shop_id={shop_id}'
    curl = f"curl '{url}' \
      -H 'authority: shopee.co.id' \
      -H 'accept: application/json' \
      -H 'accept-language: en-US,en;q=0.9' \
      -H 'content-type: application/json' \
      -H 'cookie: {cookies}' \
      -H 'priority: u=1, i' \
      -H 'sec-ch-ua: \"Chromium\";v=\"121\", \"Not A(Brand\";v=\"99\"' \
      -H 'sec-ch-ua-mobile: ?0' \
      -H 'sec-ch-ua-platform: \"macOS\"' \
      -H 'sec-fetch-dest: empty' \
      -H 'sec-fetch-mode: cors' \
      -H 'sec-fetch-site: same-origin' \
      -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36' \
      -H 'x-api-source: pc' \
      -H 'x-csrftoken: {_get_crf_token(usr)}' \
      -H 'x-requested-with: XMLHttpRequest' \
      -H 'x-sap-ri: 52757f65755ff36428a31a320101a620874b87d329f1e0ea1525' \
      -H 'x-sap-sec: 7donwtUbd63Zc63ZQb3mc6eZQb3Zc6eZc63ac63Z36cZcM3xc63Gc63ZnBqkqVZZc67ZcH3Zw6LZcKYVtHG5nFLWff5/+oiNzYvaoFiaT2de6ziTD0HuTonkqmlVNRGeMgDsPOIp4piZMYwrl4yAiy0OEVIs2+PyD/t2N5I/VDi1LwqWCgGmnzMxreToOSlSEDkOF+jEWDZmSv6BbfDVOp9cEizSsQBP9q0S5RDLq3a0WmWzmcPehdcFKmu+JY3bVuxuqMO4nEPhOQSKiFkr2X5JG1ifTIkpwsGfoziTlM25Kk84t2wE4tf5oIGobevcSkEGPWH2O11++MTBA8Oye5Re7iM3ADCRnqV4pRxZ+gUSs3A9ZthKuHPXf5S3Fq2JWA8GlwHzv5U89NXFN0vZtMnuO7TgZk/eu0QNpKch35gJoFBUWzKab8sQoiY8Qjd6rfwZ8NMdX2SBHX4QHPN2b6wWRaSl1m37ZHbQDhlaOaLoq+M9v+9A+oOdSENzAUXat6pG+1BmWN/m4eJ9ilMaExjqvB3zKx6o5EmO6ULuQmlxiIlXKoFxvuYMN+/NS+qYxfZv337BqducU6QSUH52t8ddNgPjEF8zOeKYw4u6oXJMJfLpA3A6qrI2JTOGMCwkqNWC+mqnVjRaX7OnBjArDS6cR63Zc/GSeEMILEZIc63ZcN1kqW8mc63Z+63Zc7eZc67oTNZq3VbWTKXdnayGfz+p9mKJ+HZZc63oE/ZELhKKeb3Zc63mc6UZR63Gc6ZZc63mc63Z+63Zc7eZc6/n90GfYjsssZTU3fMdQ/eUopby1VZZc63pehE/KEPJ2H3Zc6/=' \
      -H 'x-shopee-language: id' \
      -H 'x-sz-sdk-version: 3.3.0-2&1.6.8' \
      --compressed"
    try:
        process = subprocess.Popen(curl, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            response = json.loads(stdout.decode('utf-8'))
            datas = response['data']['items']
            links = [f"https://shopee.co.id/product/{d['shopid']}/{d['itemid']}" for d in datas]
            return ','.join(links)
        else:
            print(f"Error running cURL command. stderr: {stderr.decode('utf-8')}")
            return ''
    except Exception as e:
        print(f"An error occurred: {e}")
        return ''


def _get_cookies(usr: str) -> dict:
    try:
        with open(f"data/auth/shop_ee_session_{usr}.json", "r") as f:
            session = json.loads(f.read())
            cookies = session['cookies']
            return {c['name']: c['value'] for c in cookies}
    except FileNotFoundError:
        print(f"Cookies not found for {usr}. Please LOGIN first.")
        return {}
        pass


def _affiliate_headers(usr: str) -> dict:
    return {
        'authority': 'affiliate.shopee.co.id',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'affiliate-program-type': '1',
        'csrf-token': _get_crf_token(usr),
        'referer': 'https://affiliate.shopee.co.id/offer/product_offer',
        'sec-ch-ua': '"Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }


def _get_crf_token(usr: str) -> str:
    try:
        with open(f"data/auth/shop_ee_session_{usr}.json", "r") as f:
            session = json.loads(f.read())
            cookies = session['cookies']
            token_cookie = next(c for c in cookies if c['name'] == 'csrftoken')
            return token_cookie['value']

    except FileNotFoundError:
        print(f"Cookies not found for {usr}. Please LOGIN first.")
        return ''


def _login():
    parser = argparse.ArgumentParser()
    parser.add_argument('usr')
    parser.add_argument('pwd')
    args = parser.parse_args()

    usr = args.usr
    pwd = args.pwd
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://shopee.co.id/buyer/login")
        page.fill('input[name=loginKey]', usr)
        page.fill('input[name=password]', pwd)
        page.get_by_role("button", name="Log in").click()

        time.sleep(3)
        try:
            page.wait_for_url(url='https://shopee.co.id/verify/ivs?is_initial=true')
            time.sleep(60)
        except Exception as e:
            print(e)
            pass

        try:
            expect(page.get_by_role("link", name="notifikasi")).to_be_visible()
            auth_dir = 'data/auth'
            makedirs(auth_dir, exist_ok=True)
            context.storage_state(path=f"{auth_dir}/shop_ee_session_{usr}.json")

            print('Login Success')
        except Exception as e:
            print(e)
            print('Login Failed')

        browser.close()


if __name__ == '__main__':
    _login()
