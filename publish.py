import argparse
import os
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse, unquote

import pandas as pd
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy as By
from pandas import DataFrame
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import _curl
from __table import *
from _ssstik import download_tiktok_video, download_shop_ee_video

uploaded_datas = []


def _get_random_entries(count: int) -> DataFrame:
    try:
        if Path(df_file).exists():
            df = pd.read_csv(df_file)
            f_df = df[(df[C_IS_UPLOADED] == False) & (df[C_STOCK] > 1)]
            return f_df.sample(count, replace=False) if count <= len(f_df) else df

    except FileNotFoundError:
        pass


def _set_entry_uploaded(index: int) -> bool:
    try:
        if Path(df_file).exists():
            df = pd.read_csv(df_file)
            df.loc[index, C_IS_UPLOADED] = True
            df.to_csv(df_file, index=False)
            print(f'[{index + 2}] is uploaded (True)')
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
        print(f"Video pushed to {adb_videos_dir}{file_name}")
        return True
    except Exception as e:
        print(e)
        return False


def _remove_from_remote_device(video_file: str) -> bool:
    file_name = PurePosixPath(unquote(urlparse(video_file).path)).parts[-1:][0]
    try:
        os.system(f"adb shell rm {adb_videos_dir}{file_name}")
        os.system(
            f"adb shell \"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{adb_videos_dir}\"")
        print(f"Video deleted from {adb_videos_dir}{file_name}")
        return True
    except Exception as e:
        print(e)
        return False


def _set_favorite_product(product_link: str, like: bool) -> bool:
    shop_id, product_id = PurePosixPath(unquote(urlparse(product_link).path)).parts[-2:]
    print(f'Request set favorite {like} to {product_link}')
    return _curl.set_fav_product(like, shop_id, product_id)


def _publish_video(i: int, video_file: str, product_link: str, caption: str):
    if _push_to_remote_device(video_file):
        driver = webdriver.Remote(f"http://127.0.0.1:4723", options=options)
        wait = WebDriverWait(driver, 7)

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
        id_attach_product = "com.shopee.id.dfpluginshopee16:id/ll_add_product_symbol"
        id_caption = "com.shopee.id.dfpluginshopee16:id/et_caption"
        id_share_dialog = "com.shopee.id:id/md_button_layout"

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
            start_x = rect['width'] // 2
            start_y = rect['height'] * 0.8
            end_y = rect['height'] * 0.2

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
            wait.until(ec.visibility_of_element_located((By.ID, id_attach_product))).click()
            wait.until(ec.visibility_of_element_located((By.XPATH, path_affiliate_tab))).click()
            wait.until(ec.visibility_of_element_located((By.XPATH, path_fav_tab))).click()
            wait.until(ec.visibility_of_element_located((By.XPATH, path_add_product_1))).click()
            wait.until(ec.visibility_of_element_located((By.XPATH, path_done_add_product))).click()
            v_desc = wait.until(ec.visibility_of_element_located((By.ID, id_caption)))
            v_desc.click()
            v_desc.send_keys(caption)
            wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/tv_right"))).click()
            wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/btn_post"))).click()

            WebDriverWait(driver, 17).until(ec.visibility_of_element_located((By.ID, id_share_dialog)))
            driver.quit()

            # Succeed
            global uploaded_datas
            uploaded_datas.append(f'[{i + 2}] {product_link} -- {video_file}')
            print(f'\n\n((( POSTED VIDEO ))) [{i + 2}] {product_link} -- {video_file} -- {caption}\n\n')

        except Exception as e:
            print(e)

        finally:
            _remove_from_remote_device(video_file)
            _set_favorite_product(product_link, False)
            _set_entry_uploaded(i)
            print('-----------------------------------------------------------------------------------------------\n\n')


def _fallback(row: int, product_link: str, video_link: str):
    print(f'Data is not eligible: [{row}] {product_link} - {video_link}\n')
    print('-----------------------------------------------------------------------------------------------\n\n')


def _non_empty_str(val) -> bool:
    return isinstance(val, str) and bool(val.strip()) if val is not None else False


def process_data(data):
    uploaded_datas.clear()
    for i in data.index:
        product, tiktok, video, keyword = data[C_LINK][i], data[C_TIKTOK_V][i], data[C_VIDEO][i], data[C_TIKTOK_K][i]
        desc = keyword[:70] if len(keyword) >= 70 else keyword
        caption = f"#RacunShopee #ViralDiShopeeVideo  #ShopeeHaul #ShopeeDiskon #ShopeeGratisOngkir {desc}"

        if _non_empty_str(tiktok):
            tiktok_video = download_tiktok_video(tiktok, product)
            if os.path.getsize(tiktok_video) > 0 and _set_favorite_product(product, True):
                _publish_video(i, tiktok_video, product, caption)
            else:
                _fallback((i + 2), product, tiktok)

        if _non_empty_str(video):
            shop_ee_video = download_shop_ee_video(video, product)
            if os.path.getsize(shop_ee_video) > 0 and _set_favorite_product(product, True):
                _publish_video(i, shop_ee_video, product, caption)
            else:
                _fallback((i + 2), product, video)

    print('\n\n'.join(uploaded_datas))
    print(f'\nTOTAL UPLOADED: {len(uploaded_datas)}')


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
    # __reset_all_uploaded_to_false()
