import argparse
import os
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse, unquote

import pandas as pd
import requests
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy as By
from pandas import DataFrame
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from __api import affiliate_headers
from __table import *
from _ssstik import download_tiktok_video, download_shop_ee_video


def _get_random_entries(count: int) -> DataFrame:
    try:
        if Path(df_file).exists():
            df = pd.read_csv(df_file)
            f_df = df[df[C_IS_UPLOADED] == False]
            return f_df.sample(count)

    except FileNotFoundError:
        pass


def _set_entry_uploaded(index: int) -> bool:
    try:
        if Path(df_file).exists():
            df = pd.read_csv(df_file)
            df.loc[index, C_IS_UPLOADED] = True
            df.to_csv(df_file, index=False)
            return True

    except FileNotFoundError:
        pass
        return False


def _push_to_remote_device(file: str) -> bool:
    try:
        file_name = PurePosixPath(unquote(urlparse(file).path)).parts[-1:][0]
        os.system(f"adb push {file} {adb_videos_dir}{file_name}")
        os.system(
            f"adb shell \"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{adb_videos_dir}\"")
        return True
    except Exception as e:
        print(e)
        return False


def _remove_remote_video(video_file: str) -> bool:
    try:
        os.system(f"adb shell rm {video_file}")
        return True
    except Exception as e:
        print(e)
        return False


def _favorite_product(product_link: str) -> bool:
    shop_id, product_id = PurePosixPath(unquote(urlparse(product_link).path)).parts[-2:]
    data = {
        'shop_item_ids': [
            {
                'shop_id': shop_id,
                'item_id': product_id,
            },
        ],
    }

    response = requests.post('https://shopee.co.id/api/v4/pages/like_items', headers=affiliate_headers, json=data)
    return response.status_code == 200


def _publish_video(video_file: str, product_link: str, caption: str):
    if _favorite_product(product_link) and _push_to_remote_device(video_file):
        driver = webdriver.Remote(f"http://127.0.0.1:4723", options=options)
        wait = WebDriverWait(driver, 7)
        window_size = driver.get_window_size()

        # Calculate coordinates for gestures
        start_x = window_size['width'] // 2
        start_y = window_size['height'] * 0.8
        end_y = window_size['height'] * 0.2

        # Element Locator Params
        path_profile = "//android.widget.LinearLayout[@resource-id=\"com.shopee.id:id/sp_bottom_tab_layout\"]/android.widget.FrameLayout[6]"
        path_tab_video = "//android.view.ViewGroup[@resource-id=\"tabButton_Video\"]"
        path_show_all = "//android.widget.ScrollView[@resource-id=\"video\"]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]"
        path_tab_posting = "//android.view.ViewGroup[@content-desc=\"click post tab\"]"
        path_post = "//android.view.ViewGroup[@content-desc=\"click to post video\"]"
        path_edit_continue_1 = "//android.widget.TextView[@text=\"Lanjutkan\"]"
        path_affiliate_tab = "//android.widget.FrameLayout[@resource-id=\"android:id/content\"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[4]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[5]"
        path_fav_tab = "//android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.ViewGroup/android.widget.HorizontalScrollView/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup"
        path_add_product_1 = "(//android.widget.TextView[@text=\"Tambah\"])[1]"
        path_done_add_product = "//android.widget.FrameLayout[@resource-id=\"android:id/content\"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[2]"

        # Enter upload menu from Profile bottom nav
        wait.until(ec.visibility_of_element_located((By.XPATH, path_profile))).click()
        wait.until(ec.visibility_of_element_located((By.XPATH, path_tab_video))).click()
        wait.until(ec.visibility_of_element_located((By.XPATH, path_show_all))).click()
        wait.until(ec.visibility_of_element_located((By.XPATH, path_tab_posting))).click()
        wait.until(ec.visibility_of_element_located((By.XPATH, path_post))).click()
        wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id:id/ll_gallery_entrance"))).click()
        wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id:id/lyt_pick_title"))).click()

        # Find the gallery album and select video
        wait.until(ec.presence_of_all_elements_located((By.ID, "com.shopee.id:id/rv_folder")))
        album_locator = By.ANDROID_UIAUTOMATOR, 'new UiSelector().text("{}")'.format(album_name)
        while not driver.find_elements(*album_locator):
            driver.swipe(start_x, start_y, start_x, end_y, 100)
        driver.find_element(*album_locator).click()
        videos = wait.until(ec.presence_of_all_elements_located((By.ID, "com.shopee.id:id/iv_picture")))
        videos[0].click()

        # Start Posting
        wait.until(ec.visibility_of_element_located((By.XPATH, path_edit_continue_1))).click()
        wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id:id/tv_compress"))).click()
        wait.until(ec.visibility_of_element_located(
            (By.ID, "com.shopee.id.dfpluginshopee16:id/ll_add_product_symbol"))).click()
        wait.until(ec.visibility_of_element_located((By.XPATH, path_affiliate_tab))).click()
        wait.until(ec.visibility_of_element_located((By.XPATH, path_fav_tab))).click()
        wait.until(ec.visibility_of_element_located((By.XPATH, path_add_product_1))).click()
        wait.until(ec.visibility_of_element_located((By.XPATH, path_done_add_product))).click()
        v_desc = wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/et_caption")))
        v_desc.click()
        v_desc.send_keys(caption)
        wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/tv_right"))).click()
        wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/btn_post"))).click()
        wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id:id/md_button_layout")))
        driver.quit()


def process_data(data):
    for i in data.index:
        link, tiktok, video, keyword = data[C_LINK][i], data[C_TIKTOK_V][i], data[C_VIDEO][i], data[C_TIKTOK_K][i]
        desc = keyword[:70] if len(keyword) >= 70 else keyword
        caption = f"#RacunShopee #ViralDiShopeeVideo  #ShopeeHaul #ShopeeDiskon #ShopeeGratisOngkir {desc}"
        if len(tiktok) > 0:
            tiktok_video = download_tiktok_video(tiktok, link)
            _publish_video(tiktok_video, link, caption)
            _remove_remote_video(tiktok_video)
            _set_entry_uploaded(i)
            print(f'POSTED PRODUCT >>> [{i + 2}] {keyword} {link} ')

        if len(video) > 0:
            product_video = download_shop_ee_video(video, link)
            _publish_video(product_video, link, caption)
            _remove_remote_video(product_video)
            _set_entry_uploaded(i)
            print(f'POSTED PRODUCT >>> [{i + 2}] {keyword} {link} ')


def __reset_all_uploaded_to_false():
    print('!!! This should not be used in production !!!')
    try:
        if Path(df_file).exists():
            df = pd.read_csv(df_file)
            df[C_IS_UPLOADED] = False
            df.to_csv(df_file, index=False)
            print(df[C_IS_UPLOADED])

    except FileNotFoundError:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, default=5)
    args = parser.parse_args()
    count = args.count
    data = _get_random_entries(count)
    process_data(data)


if __name__ == '__main__':
    # Project File
    df_file = 'data/scrap/products.csv'

    # Remote File
    album_name = '_shop-affiliate-videos'
    adb_videos_dir = f'/sdcard/{album_name}/'

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
