import argparse
import os
import random
import re
import time
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

import numpy as np
import pandas as pd
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy as By
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import _shopee
from __table import C_LINK, C_TIKTOK_V, C_IS_UPLOADED, C_STOCK, C_TIKTOK_K, C_EST_COMM, C_TITLE
from _ssstik import download_tiktok


def __set_favorite_product(product_link: str, like: bool) -> bool:
    shop_id, product_id = PurePosixPath(unquote(urlparse(product_link).path)).parts[-2:]
    print(f'\nPerform curl to set favorite {like} to {product_link}')
    return _shopee.set_fav_product(like, shop_id, product_id)


def __push_to_remote_device(file: str) -> bool:
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


def __remove_from_remote_device(video_file: str) -> bool:
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


def __set_entry_uploaded(index: int) -> bool:
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


def __publish_video(video_file: str, caption: str, products: DataFrame):
    print(f'\n READY TO UPLOAD: {video_file} -> {products[C_LINK]} {products[C_EST_COMM]}\n')
    all_fav_true = all(__set_favorite_product(p[C_LINK], True) for i, p in products.iterrows())
    if __push_to_remote_device(video_file) & all_fav_true:
        driver = webdriver.Remote(f"http://127.0.0.1:4723", options=options)
        wait = WebDriverWait(driver, 7)

        # Element Locator Params
        path_profile = "//android.widget.LinearLayout[@resource-id=\"com.shopee.id:id/sp_bottom_tab_layout\"]/android.widget.FrameLayout[6]"
        path_tab_video = "//android.view.ViewGroup[@resource-id=\"tabButton_Video\"]"
        path_show_all = "//android.widget.ScrollView[@resource-id=\"video\"]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]"
        path_tab_posting = "//android.view.ViewGroup[@content-desc=\"click post tab\"]"
        path_post = "//android.view.ViewGroup[@content-desc=\"click to post video\"]"
        path_edit_continue_1 = "//android.widget.TextView[@text=\"Lanjutkan\"]"
        # path_sound_effect = "//android.widget.LinearLayout[@resource-id=\"com.shopee.id:id/ll_top_right_menu\"]/android.widget.LinearLayout[2]"
        # path_sound_toddler = "(//android.widget.ImageView[@resource-id=\"com.shopee.id:id/iv_bottom_window_icon\"])[4]"
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
            album_locator = By.ANDROID_UIAUTOMATOR, 'new UiSelector().text("{}")'.format(album_name)
            while not driver.find_elements(*album_locator):
                driver.swipe(center_x, bottom_y * 0.8, center_x, bottom_y * 0.2, 100)
            driver.find_element(*album_locator).click()
            videos = wait.until(ec.presence_of_all_elements_located((By.ID, "com.shopee.id:id/iv_picture")))
            videos[0].click()

            # Start Posting
            wait.until(ec.visibility_of_element_located((By.XPATH, path_edit_continue_1))).click()
            # Toddle sound effect
            # wait.until(ec.visibility_of_element_located((By.XPATH, path_sound_effect))).click()
            # wait.until(ec.visibility_of_element_located((By.XPATH, path_sound_toddler))).click()
            # wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id:id/player_container"))).click()
            wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id:id/tv_compress"))).click()

            # Caption
            v_desc = wait.until(ec.visibility_of_element_located((By.ID, id_caption)))
            v_desc.click()
            v_desc.send_keys(caption)
            wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/tv_right"))).click()

            # Loop attach products
            tagged_product = 0
            total_product = len(products)
            for i, r in enumerate(products):
                if tagged_product >= total_product:
                    break

                add_id = id_attach_product if i == 0 else id_add_more_product
                wait.until(ec.visibility_of_element_located((By.ID, add_id))).click()
                wait.until(ec.visibility_of_element_located((By.XPATH, path_affiliate_tab))).click()
                wait.until(ec.visibility_of_element_located((By.XPATH, path_fav_tab))).click()
                btn_add_locator = By.ANDROID_UIAUTOMATOR, 'new UiSelector().text(\"Tambah\")'
                found_btn = False
                n_scroll = 0
                while not found_btn and n_scroll <= 3:
                    if driver.find_elements(*btn_add_locator):
                        found_btn = True
                    else:
                        driver.swipe(center_x, bottom_y * 0.7, center_x, bottom_y * 0.3, 100)
                        n_scroll += 1

                if found_btn:
                    driver.find_element(*btn_add_locator).click()
                    wait.until(ec.visibility_of_element_located((By.XPATH, path_done_add_product))).click()
                    tagged_product += 1

                else:
                    # No more products to add
                    driver.press_keycode(4)
                    break

            # Save to Draft
            wait.until(
                ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/tv_drafts_box"))).click()

            # Succeed
            for i in products.index:
                __set_entry_uploaded(i)

            uploaded_tiktok.append(f'{video_file} -- {products}')
            print(f'\n\n((( Video Saved to Draft ))) {video_file} for {len(products)} products \n\n')

        except Exception as e:
            # Only remove video for unpublished draft
            __remove_from_remote_device(video_file)
            print(e)

        finally:
            # No longer needed to remove video from device since it still used for Draft feature
            # __remove_from_remote_device(video_file)

            all(__set_favorite_product(p[C_LINK], False) for i, p in products.iterrows())
            driver.quit()
            print('-----------------------------------------------------------------------------------------------\n\n')
    else:
        all(__set_favorite_product(p[C_LINK], False) for i, p in products.iterrows())


def __first_n_words(words: str):
    words = re.findall(r'\b\w+\b', words)
    return ' '.join(words[:3])


def _get_random_entries(limit: int = 0) -> DataFrameGroupBy:
    if Path(df_file).exists():
        df = pd.read_csv(df_file)
        # get uploaded False and stock > 1
        filtered = df[(df[C_IS_UPLOADED] == False) & (df[C_STOCK] > 1)]
        # only take group that has > 2 rows
        filtered_len = filtered.groupby(df[C_TIKTOK_V]).filter(lambda x: len(x) > 2)
        grouped = filtered_len.groupby(df[C_TIKTOK_V])

        # Limit Group by Request
        if 0 < limit < len(grouped):
            group_limit = min(limit, len(grouped))
            random_names = np.random.choice(list(grouped.groups.keys()), group_limit, replace=False)
            selected_groups = [grouped.get_group(group_name) for group_name in random_names]
            return pd.concat(selected_groups).groupby(df[C_TIKTOK_V])
        else:
            return grouped


def _non_empty_file(file) -> bool:
    path = Path(file)
    return path.stat().st_size > 0 if path.is_file() is not None else False


def generate_hashtags() -> str:
    hashtags = '#RacunShopee #ViralDiShopeeVideo #BadaiTapiBudget #SultanShopeeVideo'.split()
    random.shuffle(hashtags)
    return ' '.join(hashtags)


def process_data(datas: DataFrameGroupBy):
    uploaded_tiktok.clear()
    for tiktok_url, rows in datas:
        # take max 5 products to attach, the rest will not be published
        filtered_df = rows.sort_values(by=C_EST_COMM).head(5)

        first = filtered_df.iloc[0]
        tiktok_keyword = first[C_TIKTOK_K]
        title = first[C_TITLE]
        brand_hashtag = str(tiktok_keyword).split()[0]

        hashtags = f'#{brand_hashtag} {generate_hashtags()}'
        remaining_len = 149 - len(hashtags)

        desc = title[:remaining_len] if len(title) >= remaining_len else title
        caption = f"{desc} {hashtags}"

        tiktok_video = download_tiktok(str(tiktok_url))
        if _non_empty_file(tiktok_video):
            __publish_video(tiktok_video, caption, filtered_df)
        else:
            indexes = rows.index
            print(f'Cant upload video: {indexes} {tiktok_video}\n')
            print(
                '-------------------------------------------------------------------------------------------\n\n')
    print(f'\nTOTAL UPLOADED: {len(uploaded_tiktok)}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", "-l", help="Limit the video count to upload", type=int, default=0)
    args = parser.parse_args()
    limit = args.limit

    datas = _get_random_entries(limit)
    if len(datas) <= 0:
        print('No available data. Run collect.py to get more data.')
    else:
        process_data(datas)


if __name__ == '__main__':
    uploaded_tiktok = []

    # Project File
    df_file = 'data/scrap/products.csv'

    # Remote File
    album_name = '_tiktok_videos'
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
