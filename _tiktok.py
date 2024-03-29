import argparse
import contextlib
import re
import time
import urllib.parse
from argparse import Namespace
from os import makedirs

from parsel import Selector
from playwright.sync_api import sync_playwright, Page, expect


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

        time.sleep(3)
        try:
            page.locator(".captcha_verify_bar").is_visible()
            time.sleep(17)
        except Exception as e:
            print(e)
            pass

        try:
            expect(page.locator('#header-more-menu-icon')).to_be_visible()
            auth_dir = 'data/auth'
            makedirs(auth_dir, exist_ok=True)
            context.storage_state(path=f"{auth_dir}/tiktok_session_{username}.json")
            print('Login Success')
        except Exception as e:
            print(e)
            print('Login Failed')

        browser.close()


@contextlib.contextmanager
def __tiktok_page(headless: bool = True) -> tuple[Page]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        try:
            context = browser.new_context(storage_state=f"data/auth/tiktok_session_ware.stock.json")
            yield context.new_page()
        except RuntimeError as e:
            print(e)
        browser.close()


def get_tiktok_link(keyword: str, is_headless: bool = True) -> tuple[str, list[str]]:
    clean_keyword = re.sub(r'\b' + re.escape('sexy') + r'\b', 'seksi', keyword, flags=re.IGNORECASE)
    encoded_keywords = urllib.parse.quote(clean_keyword)
    print(f"Search tiktok links for {keyword}")
    with __tiktok_page(headless=is_headless) as (page):
        page.goto(f"https://www.tiktok.com/search/video?q={encoded_keywords}")

        if is_headless:
            time.sleep(5)
        else:
            time.sleep(17)

        if is_headless and page.locator('div[id=tiktok-verify-ele]').count() > 0:
            print('Captcha Detected')
            exit(1)
        else:
            list_video = page.wait_for_selector('div[id=tabs-0-panel-search_video]', timeout=10 * 1000)
            # List of Selectors -> <Selector query='@href' data='https://www....'>
            links = Selector(text=list_video.inner_html()).css('a').xpath('@href').getall()
            # pics = Selector(text=list_video.inner_html()).css('img').xpath('@srcset').getall()
            # print(pics)

            # Filter video links
            results = [link for link in links if link.startswith("https://www.tiktok.com/@")]
            # return keyword, results[:5]
            return keyword, results


if __name__ == '__main__':
    __login()
