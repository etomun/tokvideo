import argparse
import json
from argparse import Namespace
from os import makedirs

from playwright.sync_api import sync_playwright


def __get_args() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('password')
    return parser.parse_args()


def __login():
    args = __get_args()
    username = args.username
    pwd = args.password
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://shopee.co.id/buyer/login?next=https%3A%2F%2Faffiliate.shopee.co.id")
        page.fill('input[name=loginKey]', username)
        page.fill('input[name=password]', pwd)
        page.get_by_role("button", name="Log in").click()

        # Manual captcha
        # time.sleep(15)

        auth_dir = 'data/auth'
        makedirs(auth_dir, exist_ok=True)
        with open(f"{auth_dir}/affiliate_cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))
            print("Login Succeed")

        browser.close()


def get_cookies():
    try:
        with open("data/auth/affiliate_cookies.json", "r") as f:
            cookies = json.loads(f.read())
            return {c["name"]: c["value"] for c in cookies}

    except FileNotFoundError:
        pass


if __name__ == '__main__':
    __login()
    print(get_cookies())
