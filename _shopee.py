import argparse
import json
import subprocess
from os import makedirs

from playwright.sync_api import sync_playwright


def set_fav_product(is_fav: bool, shop_id: str, product_id: str) -> bool:
    endpoint = 'like_items' if is_fav else 'unlike_items'

    # with open("data/auth/shopee_cookies.json", "r") as f:
    #     json_cookies = json.loads(f.read())
    #     cookies = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in json_cookies])

    cookies = '__LOCALE__null=ID; csrftoken=bZ4aC5e1qrOzU0NJIHKgP7Xmpfm3Egg8; _fbp=fb.2.1671691525641.722325261; _tt_enable_cookie=1; _ttp=HA3wQHY3B2CtgbRVrph8LTlSuAo; _QPWSDCXHZQA=171a5039-0119-41eb-fceb-fc2fe0164fde; _fbc=fb.2.1672629331899.IwAR1LPjC1cr3R5AlQzkRBhMKQvQ4hjr6bNrmQT8tY9HRqCOT91qCa9N0LmCk; SPC_CLIENTID=UmFmV1U0N2x3YmxGvymyjxlcqjtzndzs; SPC_IA=1; __stripe_mid=938c8899-a191-4af3-b9c3-6cdbca6f4a7eba1d10; language=en; SPC_F=PotThYhfyczry0d8dc4LABk1KI85fFUV; REC_T_ID=d8b5a598-4deb-11ee-809f-f4ee08261793; _gcl_au=1.1.624132024.1696216583; _gcl_aw=GCL.1696906138.CjwKCAjwyY6pBhA9EiwAMzmfwRK__bb04KI6gb_9PJTZIwcow5Fvu_cwa_Li4bgGyxh1rmZYpD-qvBoCeG4QAvD_BwE; _gac_UA-61904553-8=1.1696906139.CjwKCAjwyY6pBhA9EiwAMzmfwRK__bb04KI6gb_9PJTZIwcow5Fvu_cwa_Li4bgGyxh1rmZYpD-qvBoCeG4QAvD_BwE; _ga_8TJ45E514C=GS1.1.1698424089.4.1.1698424729.60.0.0; SC_DFP=mXXvwSbOxnItOxaqBkCkvGiQMaDEXwbk; SPC_SC_SA_TK=; SPC_SC_SA_UD=; _med=affiliates; _sapid=fa8af575-4dfb-400e-8211-1ed4bf735d2a; SPC_SC_TK=604e11f8b6bcc1ec6fe5433bee0a2934; SPC_SC_UD=1098761675; SPC_STK=VOJrhoORw36Wu3gipUWKUym1UpQs7+uNcdz2JSABZkRjCIDveJbg9AP3etjljxB54GQrhbCSYeLtpE9BPh6CM9GeKBYTWFtqwK6yxTMdSHn30eulJGwSKdAi1bTdigWNRTZNNQboao2P0y70dqzGW9wNMf6LgFQrY1vXbxl8xO6uZBA02AK6ovFg6WHbdq82; _ga_QMX630BLLS=GS1.1.1701362631.4.0.1701362643.48.0.0; SPC_SEC_SI=v1-QkVNTXZRVGlzMDVhZ3NjRUQLQVgTtuDVi2HqVMBU1PuGOgJ1o5MgbqVTFBgd/2my5Rt7q/Zn0bn5lTbe3CgJer6f0irMV5wGxLO0QCTMocw=; SPC_SI=6mRoZQAAAABoNFFHdnpQYZyWPgIAAAAAWmlHcGxIOTM=; REC7iLP4Q=a477373d-daa9-4384-b48e-c4ead5b2ec13; _gid=GA1.3.429524072.1701854478; AMP_TOKEN=%24NOT_FOUND; _dc_gtm_UA-61904553-8=1; SPC_ST=.YTNlWXgwSWxjYklCQUFOMKosF7HsN1hdmZzCmK8hQaC89j9q/6DcBl2ARJzzVgbn8wH/+19Xz2NMVL/sckwdO1TxGBiVPl80tUH2mZXICloAdust29jWhsHKNfqXmomRgqPdjwdmXyU0g07TaSqDrE/MndR0+sVuB0DBaqnTJqkkzldEbf7zVVQFQXE28NWZOE8Pga/I5hTCnn+T9WwnGg==; SPC_U=1098761675; SPC_R_T_ID=Qma4E3LjUN6xYSz7MM0T7k2TD+rCDP4z8TkA2zl26kQJCA2STkczCG5/akJaO5lLFypox2X6XMGrLhFMu0RajnyX/hTVaUePP9vUFfTAWaiNvBtC7Db6EA6Msb5V3lvVkrV5DCFQCLlf0WeT6SKd9hN7CWJlq8js44hdeVKiZI0=; SPC_R_T_IV=Vk95ZzRlSnVWdnpYSGJJNg==; SPC_T_ID=Qma4E3LjUN6xYSz7MM0T7k2TD+rCDP4z8TkA2zl26kQJCA2STkczCG5/akJaO5lLFypox2X6XMGrLhFMu0RajnyX/hTVaUePP9vUFfTAWaiNvBtC7Db6EA6Msb5V3lvVkrV5DCFQCLlf0WeT6SKd9hN7CWJlq8js44hdeVKiZI0=; SPC_T_IV=Vk95ZzRlSnVWdnpYSGJJNg==; _ga=GA1.3.2066265449.1671691526; shopee_webUnique_ccd=%2BePslPx6GLaLgS2VvUKQaQ%3D%3D%7C4qdY3pcwnrkC6AUWme2%2FzyRFdMnYneyMk%2BqgBXQTFWVJnikYrJ3dpv9vvBHqcdCFD6bO2lteBg0%3D%7Ch1vBA0gFS5za0bBt%7C08%7C3; ds=93fb7fdca2ecbff886f5f68aa6c40e0a; SPC_EC=ajlSenNIWVRkVUhhSGVJWayZmiVNqbDevmcUijP176D66Lm8AyFmIhHdG8Bvwu+3sbyOXTiAaz4ih3ttL321gb/iz9yvh5QCUHcp06QfPXndgI/bvZNS8bVeOcLiN9ID4YUCX0FAJK0fNaK4xlEHiPOH8NFC5fYtSZVyGDracH8=; _ga_SW6D8G0HXK=GS1.1.1701865017.143.1.1701865217.32.0.0'

    curl_command = [
        'curl',
        '-X', 'POST',
        f'https://shopee.co.id/api/v4/pages/{endpoint}',
        '-H', 'authority: shopee.co.id',
        '-H', 'accept: application/json',
        '-H', 'accept-language: en-US,en;q=0.9',
        '-H', 'content-type: application/json',

        '-H', 'if-none-match-: 55b03-ea8c9f1ba75cb000a410ab50e9378bcc',
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
        process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

        # Manual captcha
        # time.sleep(15)

        auth_dir = 'data/auth'
        makedirs(auth_dir, exist_ok=True)
        with open(f"{auth_dir}/shopee_cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))
            print("Login Succeed")

        browser.close()


if __name__ == '__main__':
    _login()
