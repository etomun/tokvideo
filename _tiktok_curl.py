import contextlib
import json
import re
import subprocess
import urllib.parse

from playwright.sync_api import sync_playwright, Page


def capture_curl_command(route, request):
    curl_command = f"curl {request.method} '{request.url}' \\\n"

    # Add headers to the cURL command
    headers = request.headers
    curl_command += f" -H 'authority: www.tiktok.com' \\\n"
    curl_command += f" -H 'accept-language: en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7,id;q=0.6' \\\n"
    curl_command += f" -H 'cache-control: max-age=0' \\\n"
    for name, value in headers.items():
        curl_command += f" -H '{name}: {value}' \\\n"

    # curl_command += f" -H 'sec-fetch-dest: document' \\\n"
    # curl_command += f" -H 'sec-fetch-mode: navigate' \\\n"
    # curl_command += f" -H 'sec-fetch-user: ?1' \\\n"
    curl_command += '--compressed'

    # If it's a POST request, include the request body
    if request.method.upper() == 'POST':
        pass
        # post_data = request.post_data
        # if post_data:
        #     curl_command += f" -d '{post_data}'"

    # Append the cURL command to the list
    intercepted_curls.append(curl_command)

    # Continue with the intercepted request
    route.continue_()


@contextlib.contextmanager
def __tiktok_page(headless: bool = True) -> tuple[Page]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        context.route('**/*', lambda route, request: capture_curl_command(route, request))
        try:
            with open("data/auth/tiktok_cookies.json", "r") as f:
                cookies = json.loads(f.read())
                context.add_cookies(cookies)
        except FileNotFoundError:
            pass
        yield context.new_page()
        browser.close()


def __int(str_val: str) -> int:
    return int(re.sub(r"\D", "", str_val))


def __filter_video(v: dict) -> bool:
    v_id = v['id']

    filter_ratio = v['video']['height'] > v['video']['width']
    filter_duration = 30 >= v['video']['duration'] > 2
    filter_play_count = v['stats']['playCount'] < 6000
    filter_follower_count = v['authorStats']['followerCount'] < 10000

    if not filter_ratio:
        print(f"{v_id}: invalid ration")
    if not filter_duration:
        print(f"{v_id}: invalid duration")
    if not filter_play_count:
        print(f"{v_id}: invalid play count")
    if not filter_follower_count:
        print(f"{v_id}: invalid follower count")

    return filter_ratio and filter_duration and filter_play_count and filter_follower_count


def _run_curl(curl_command: str) -> list:
    print(curl_command)
    try:
        process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Check if successful (exit code 0)
        if process.returncode == 0:
            response = json.loads(stdout.decode('utf-8'))
            videos = response['item_list']
            if len(videos) <= 0:
                print(response)
            f = list(filter(__filter_video, videos))
            return list(map(lambda r: f"https://www.tiktok.com/@{r['author']['uniqueId']}/video/{r['video']['id']}", f))

        else:
            print(f"Error running cURL command. stderr: {stderr.decode('utf-8')}")
            return []

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_tiktok_v_url(keyword: str) -> list:
    with __tiktok_page(headless=False) as (page):
        intercepted_curls.clear()
        page.goto(f"https://www.tiktok.com/search/video?q={urllib.parse.quote(keyword)}")

        for i, curl in enumerate(intercepted_curls):
            if 'api/search/item/full' in curl:
                return _run_curl(curl)


if __name__ == '__main__':
    intercepted_curls = []
    print(get_tiktok_v_url('Skitchen Skillet Memasak ngakak'))
