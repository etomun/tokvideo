import argparse
import os
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy as By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from _shopee import set_fav_product
from _ssstik import download_tiktok
from util import delete_file


def __push_to_remote_device(file: str, album_name: str) -> bool:
    try:
        file_name = PurePosixPath(unquote(urlparse(file).path)).parts[-1:][0]
        remote_file = f'{adb_videos_dir}/{album_name}/{file_name}'
        os.system(f'adb push {file} {remote_file}')
        os.system(f'adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote_file}')
        print(f"Video pushed to {remote_file}")
        return True
    except Exception as e:
        print(e)
        return False


def __remove_from_remote_device(video_file: str, album_name: str) -> bool:
    try:
        file_name = PurePosixPath(unquote(urlparse(video_file).path)).parts[-1:][0]
        remote_file = f'{adb_videos_dir}/{album_name}/{file_name}'
        os.system(f'adb shell rm {remote_file}')
        os.system(f'adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote_file}')
        print(f'Video deleted from {remote_file}')
        return True
    except Exception as e:
        print(e)
        return False


def __publish_video(video_file: str, caption: str, product_links: list):
    all_fav_true = all(set_fav_product(usr, link, True) for link in product_links)
    album = PurePosixPath(unquote(urlparse(video_file).path)).parts[-1:][0].split('.')[-2:][0]
    if __push_to_remote_device(video_file, album) & all_fav_true:
        driver = webdriver.Remote(f"http://127.0.0.1:4723", options=options)
        wait = WebDriverWait(driver, 7)
        print(f'\nUploading video for {len(product_links)} products...')
        print(f'Make sure Shopee app is logged in for username: {usr}')

        # Element Locator Params
        path_profile = "//android.widget.LinearLayout[@resource-id=\"com.shopee.id:id/sp_bottom_tab_layout\"]/android.widget.FrameLayout[6]"
        path_tab_video = "//android.view.ViewGroup[@resource-id=\"tabButton_Video\"]"
        path_show_all = "//android.widget.ScrollView[@resource-id=\"video\"]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]"
        path_tab_posting = "//android.view.ViewGroup[@content-desc=\"click post tab\"]"
        path_post = "//android.view.ViewGroup[@content-desc=\"click to post video\"]"
        path_edit_continue_1 = "//android.widget.TextView[@text=\"Lanjutkan\"]"
        path_affiliate_tab = "//android.widget.FrameLayout[@resource-id=\"android:id/content\"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[4]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[5]"
        path_fav_tab = "//android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.ViewGroup/android.widget.HorizontalScrollView/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup"
        path_done_add_product = "//android.widget.FrameLayout[@resource-id=\"android:id/content\"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[2]"
        id_attach_product = "com.shopee.id.dfpluginshopee16:id/ll_add_product_symbol"
        id_add_more_product = "com.shopee.id.dfpluginshopee16:id/tv_add_more"
        id_caption = "com.shopee.id.dfpluginshopee16:id/et_caption"

        try:
            # Enter upload menu from Profile bottom nav
            wait.until(ec.visibility_of_element_located((By.XPATH, path_profile))).click()
            wait.until(ec.visibility_of_element_located((By.XPATH, path_tab_video))).click()
            wait.until(ec.visibility_of_element_located((By.XPATH, path_show_all))).click()
            wait.until(ec.visibility_of_element_located((By.XPATH, path_tab_posting))).click()
            wait.until(ec.visibility_of_element_located((By.XPATH, path_post))).click()
            wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id:id/ll_gallery_entrance"))).click()
            wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id:id/lyt_pick_title"))).click()

            # Find the gallery album and select video
            rect = driver.get_window_size()
            center_x = rect['width'] // 2
            bottom_y = rect['height']

            wait.until(ec.presence_of_all_elements_located((By.ID, "com.shopee.id:id/rv_folder")))
            album_locator = By.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{album}")'
            while not driver.find_elements(*album_locator):
                driver.swipe(center_x, bottom_y * 0.8, center_x, bottom_y * 0.2, 70)
            driver.find_element(*album_locator).click()
            videos = wait.until(ec.presence_of_all_elements_located((By.ID, "com.shopee.id:id/iv_picture")))
            videos[0].click()

            # Start Posting
            wait.until(ec.visibility_of_element_located((By.XPATH, path_edit_continue_1))).click()
            wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id:id/tv_compress"))).click()

            # Caption
            v_desc = wait.until(ec.visibility_of_element_located((By.ID, id_caption)))
            v_desc.click()
            v_desc.send_keys(caption)
            wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/tv_right"))).click()

            # Loop attach products
            tagged_product = 0
            total_product = len(product_links)
            for i, link in enumerate(product_links):
                if tagged_product >= total_product:
                    break

                add_id = id_attach_product if i == 0 else id_add_more_product
                wait.until(ec.visibility_of_element_located((By.ID, add_id))).click()

                for _ in range(3):
                    try:
                        wait.until(ec.visibility_of_element_located((By.XPATH, path_affiliate_tab))).click()
                        break
                    except:
                        driver.back()
                        wait.until(ec.visibility_of_element_located((By.ID, add_id))).click()
                        pass

                wait.until(ec.visibility_of_element_located((By.XPATH, path_fav_tab))).click()
                max_scroll_attempts = 2
                for _ in range(max_scroll_attempts + 1):
                    found = False
                    try:
                        locator = By.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Tambah")'
                        WebDriverWait(driver, 2).until(ec.visibility_of_element_located(locator)).click()
                        found = True
                    except:
                        if _ < max_scroll_attempts:
                            driver.swipe(center_x, bottom_y * 0.5, center_x, bottom_y * 0.2, 100)
                        else:
                            driver.back()
                            break
                    finally:
                        if found:
                            wait.until(ec.visibility_of_element_located((By.XPATH, path_done_add_product))).click()
                            tagged_product += 1
                            break

            # Save to Draft
            wait.until(
                ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/tv_drafts_box"))).click()

            # Succeed
            delete_file(video_file)
            print(f'\n\n((( Video Saved to Draft ))) {video_file} for {len(product_links)} products \n\n')

        except Exception as e:
            __remove_from_remote_device(video_file, album)
            print(e)

        finally:
            all(set_fav_product(usr, link, False) for link in product_links)
            driver.quit()
    else:
        all(set_fav_product(usr, link, False) for link in product_links)


def _non_empty_file(file) -> bool:
    path = Path(file)
    return path.stat().st_size > 0 if path.is_file() is not None else False


def main():
    tiktok = args.tiktok
    caption = args.caption.replace('-', ' ')
    products = args.products.split(',')

    video = download_tiktok(tiktok)
    if _non_empty_file(video):
        __publish_video(video, caption, products)
    else:
        print(f'Cant upload video: {video}\n')
        print('-----------------------------------------------------------------------------------------\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Shopee Username", type=str)
    parser.add_argument("tiktok", help="Tiktok Link", type=str)
    parser.add_argument("products", help="Product Links, separated with '-'", type=str)
    parser.add_argument("--caption", '-c', help="Caption with hashtags", type=str, default='')
    args = parser.parse_args()
    usr = args.username

    # Remote File
    adb_videos_dir = '/sdcard/_affiliate_videos'

    # Appium
    capabilities = {
        "platformName": "android",
        "appium:deviceName": "192.168.18.4:5555 (13)",
        "appium:automationName": "UiAutomator2",
        "appium:appPackage": "com.shopee.id",
        "appium:appActivity": "com.shopee.app.ui.home.HomeActivity_",
        "appium:noReset": True,
        "appium:shouldTerminateApp": True,
        "appium:disableWindowAnimation": True
    }
    options = UiAutomator2Options().load_capabilities(capabilities)
    main()
