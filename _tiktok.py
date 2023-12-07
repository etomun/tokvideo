import argparse
import contextlib
import json
import time
from argparse import Namespace
from os import makedirs

from parsel import Selector
from playwright.sync_api import sync_playwright, Page


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

        page.goto("https://www.tiktok.com/")
        page.locator("#header-login-button").click()

        page.get_by_role("link", name="Use phone / email / username").click()
        page.get_by_role("link", name="Log in with email or username").click()
        page.fill('input[name=username]', username)
        page.fill('input[type=password]', pwd)
        page.get_by_label("Log in").get_by_role("button", name="Log in").click()
        # Manual captcha
        time.sleep(15)
        print("Login Succeed")

        auth_dir = 'data/auth'
        makedirs(auth_dir, exist_ok=True)
        with open(f"{auth_dir}/tiktok_cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))

        context.close()
        browser.close()


@contextlib.contextmanager
def __tiktok_page(headless: bool = True) -> tuple[Page]:
    with sync_playwright() as playwright:
        context = playwright.chromium.launch(headless=headless).new_context()
        try:
            with open("data/auth/tiktok_cookies.json", "r") as f:
                cookies = json.loads(f.read())
                context.add_cookies(cookies)
        except FileNotFoundError:
            pass
        yield context.new_page()
        context.close()


def get_tiktok_url(keyword: str, is_headless: bool = True) -> str:
    with __tiktok_page(headless=is_headless) as (page):
        page.goto(f"https://www.tiktok.com/search/video?q={keyword} #howto")

        # HEADED (headless=False) for captcha):
        if not is_headless:
            time.sleep(17)

        if is_headless and page.locator('div[id=tiktok-verify-ele]').count() > 0:
            print('Captcha Detected')
            exit(0)
        else:
            time.sleep(3)
            list_video = page.wait_for_selector('div[id=tabs-0-panel-search_video]', timeout=10 * 1000)
            return Selector(text=list_video.inner_html()).css('a').xpath('@href').get()

            # selector = 'div[data-e2e="search_video-item-list"]'
            # div_videos = page.wait_for_selector(selector, timeout=10 * 1000).inner_html()
            # soup = BS(div_videos, 'html.parser')
            # links = []
            # for link in soup.find_all('a', href=lambda href: href and 'https://www.tiktok.com/@' in href):
            #     links.append(link['href'])
            # print(links)
            # return links


def _get_cookies():
    try:
        with open("data/auth/affiliate_cookies.json", "r") as f:
            cookies = json.loads(f.read())
            return {c["name"]: c["value"] for c in cookies}

    except FileNotFoundError:
        pass


if __name__ == '__main__':
    # print(_get_cookies())
    # print(get_tiktok_url('Koch'))
    __login()
