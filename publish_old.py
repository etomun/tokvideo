import argparse
import os
import random
import re
import time
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse, unquote

import pandas as pd
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy as By
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import _shopee
from __table import *
from _ssstik import download_tiktok_video, download_shop_ee_video

uploaded_datas = []


def _first_n_words(words: str):
    words = re.findall(r'\b\w+\b', words)
    return ' '.join(words[:3])


def _get_random_entries(count: int, additional_count: int = 0) -> DataFrameGroupBy:
    if Path(df_file).exists():
        df = pd.read_csv(df_file)
        cond_1 = (df[C_IS_UPLOADED] == False) & (df[C_STOCK] > 1)
        random_1 = df[cond_1].sample(count, replace=True) if count <= len(df[cond_1]) else df

        # Append similar products
        additional_rows = pd.DataFrame()
        for i, row in random_1.iterrows():
            tiktok_keywords = _first_n_words(row[C_TIKTOK_K])
            cond_2 = cond_1 & df[C_TIKTOK_K].str.contains(tiktok_keywords) & (df.index != i)
            random_2 = df[cond_2].sample(n=additional_count, replace=True) if len(df[cond_2]) > 0 else pd.DataFrame()
            additional_rows = pd.concat([additional_rows, random_2]).drop_duplicates(subset=C_LINK)

        # combined = pd.concat([random_1, additional_rows], ignore_index=True, verify_integrity=True)
        combined = pd.concat([random_1, additional_rows]).drop_duplicates(subset=C_LINK)
        return combined.groupby(df[C_TIKTOK_K].apply(_first_n_words))


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
    print(f'\nPerform curl to set favorite {like} to {product_link}')
    return _shopee.set_fav_product(like, shop_id, product_id)


def _publish_video(video_file: str, caption: str, products: DataFrame):
    all_fav_true = all(_set_favorite_product(p[C_LINK], True) for i, p in products.iterrows())
    if _push_to_remote_device(video_file) & all_fav_true:
        driver = webdriver.Remote(f"http://127.0.0.1:4723", options=options)
        wait = WebDriverWait(driver, 7)

        # Element Locator Params
        path_profile = "//android.widget.LinearLayout[@resource-id=\"com.shopee.id:id/sp_bottom_tab_layout\"]/android.widget.FrameLayout[6]"
        path_tab_video = "//android.view.ViewGroup[@resource-id=\"tabButton_Video\"]"
        path_show_all = "//android.widget.ScrollView[@resource-id=\"video\"]/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]"
        path_tab_posting = "//android.view.ViewGroup[@content-desc=\"click post tab\"]"
        path_post = "//android.view.ViewGroup[@content-desc=\"click to post video\"]"
        path_edit_continue_1 = "//android.widget.TextView[@text=\"Lanjutkan\"]"
        path_sound_effect = "//android.widget.LinearLayout[@resource-id=\"com.shopee.id:id/ll_top_right_menu\"]/android.widget.LinearLayout[2]"
        path_sound_toddler = "(//android.widget.ImageView[@resource-id=\"com.shopee.id:id/iv_bottom_window_icon\"])[4]"
        path_affiliate_tab = "//android.widget.FrameLayout[@resource-id=\"android:id/content\"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[4]/android.view.ViewGroup[2]/android.view.ViewGroup/android.view.ViewGroup[5]"
        path_fav_tab = "//android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.ViewGroup/android.widget.HorizontalScrollView/android.view.ViewGroup/android.view.ViewGroup[3]/android.view.ViewGroup"
        # path_add_product_1 = "(//android.widget.TextView[@text=\"Tambah\"])[1]"
        path_done_add_product = "//android.widget.FrameLayout[@resource-id=\"android:id/content\"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.view.ViewGroup[2]"
        id_attach_product = "com.shopee.id.dfpluginshopee16:id/ll_add_product_symbol"
        id_add_more_product = "com.shopee.id.dfpluginshopee16:id/tv_add_more"
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
            wait.until(ec.visibility_of_element_located((By.XPATH, path_sound_effect))).click()
            wait.until(ec.visibility_of_element_located((By.XPATH, path_sound_toddler))).click()
            wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id:id/player_container"))).click()
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

            # POST
            # wait.until(ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/btn_post"))).click()
            # WebDriverWait(driver, 21).until(ec.visibility_of_element_located((By.ID, id_share_dialog)))

            # DRAFT
            wait.until(
                ec.visibility_of_element_located((By.ID, "com.shopee.id.dfpluginshopee16:id/tv_drafts_box"))).click()

            # Succeed
            for i in products.index:
                _set_entry_uploaded(i)

            global uploaded_datas
            uploaded_datas.append(f'{video_file} -- {products}')
            print(f'\n\n((( VIDEO UPLOADED ))) {video_file} for {len(products)} products \n\n')

        except Exception as e:
            print(e)

        finally:
            _remove_from_remote_device(video_file)
            all(_set_favorite_product(p[C_LINK], False) for i, p in products.iterrows())
            driver.quit()
            print('-----------------------------------------------------------------------------------------------\n\n')
    else:
        all(_set_favorite_product(p[C_LINK], False) for i, p in products.iterrows())


def _non_empty_str(val) -> bool:
    return isinstance(val, str) and bool(val.strip()) if val is not None else False


def _non_empty_file(file) -> bool:
    path = Path(file)
    return path.stat().st_size > 0 if path.is_file() is not None else False


def generate_hashtags() -> str:
    hashtags = '#RacunShopee #ViralDiShopeeVideo #BadaiTapiBudget #SultanShopeeVideo'.split()
    random.shuffle(hashtags)
    return ' '.join(hashtags)


def process_data(datas: DataFrameGroupBy):
    uploaded_datas.clear()

    # data is DataFrame containing multiple rows
    for group, data in datas:
        # choose one with the highest commission
        # i = data[C_EST_COMM].idxmax()
        # d = data.loc[i]
        for i, d in data.iterrows():
            product, tiktok, video, keyword = d[C_LINK], d[C_TIKTOK_V], d[C_VIDEO], d[C_TIKTOK_K]
            desc = keyword[:70] if len(keyword) >= 70 else keyword
            caption = f"{desc} {generate_hashtags()}"

            if _non_empty_str(tiktok):
                tiktok_video = download_tiktok_video(tiktok, product)
                if _non_empty_file(tiktok_video):
                    _publish_video(tiktok_video, caption, data)
                else:
                    print(f'Cant upload video: [{i}] {tiktok_video}\n')
                    print(
                        '-------------------------------------------------------------------------------------------\n\n')
            elif _non_empty_str(video):
                shop_video = download_shop_ee_video(video, product)
                if _non_empty_file(shop_video):
                    _publish_video(shop_video, caption, data)
                else:
                    print(f'Data is not eligible: [{i}] {shop_video}\n')
                    print(
                        '-------------------------------------------------------------------------------------------\n\n')

    print(f'\nTOTAL UPLOADED: {len(uploaded_datas)}')


def _confirm_upload(datas: DataFrameGroupBy):
    print(f"\nUpload these {len(datas)} video(s)?")
    for n, g in datas:
        print(f'{n} -> {len(g)} products')
    confirmation = input("\n(Y/N): ")
    if confirmation.lower() == 'y':
        process_data(datas)
    else:
        print("[CANCELLED]")


def _replace_link(datas: DataFrameGroupBy, old_link: str, new_link: str):
    df = pd.concat([group for name, group in datas], ignore_index=True)
    df.loc[df[C_LINK] == old_link, C_LINK] = new_link
    return df.groupby(df[C_TIKTOK_K].apply(_first_n_words))


def _is_product_link_valid(user_input: str) -> bool:
    regex_pattern = r'https://shopee\.co\.id/product/\d+/\d+'
    if re.match(regex_pattern, user_input):
        return True
    else:
        return False


def _edit_links(datas: DataFrameGroupBy):
    new_datas = datas
    while True:
        cases = {}
        index = 1
        for group, d in new_datas:
            print(group)
            for i, r in d.iterrows():
                print(f'{index} {r[C_LINK]} {r[C_TIKTOK_K]}')
                cases[f'{index}'] = (_replace_link, r[C_LINK])
                index += 1

        print('Press ENTER to finish editing.')
        user_input = input("Enter the number followed by new link, example: 3 https://your.new/link: ")
        user_input_split = user_input.split()
        if len(user_input_split) == 2:
            option, param = user_input_split
            if _is_product_link_valid(param):
                selected_case = cases.get(option)
                if selected_case:
                    func, old_link = selected_case
                    new_datas = func(new_datas, old_link, param)
                else:
                    print("Invalid option. Please try again.")
            else:
                print('Invalid link. Please try again.')

        else:
            _confirm_data(new_datas)
            break


def _confirm_data(datas: DataFrameGroupBy):
    print(f'\n{len(datas)} videos to be uploaded:')
    for group, d in datas:
        print(f'- [{len(d)} products] {group}: {d[C_TIKTOK_K].tolist()}')
    print("\nOptions: ")
    print("1 Exclude Single Product")
    print("2 Edit Links")
    print("0 Cancel Upload")
    print("")
    choice = input("Or press ENTER to Upload ")

    if choice.strip() == '1':
        filtered = datas.filter(lambda g: len(g) > 1)
        grouped = filtered.groupby(filtered[C_TIKTOK_K].apply(_first_n_words))
        if len(grouped) > 0:
            _confirm_upload(grouped)
        else:
            print("No grouped products found.")
    elif choice.strip() == '2':
        _edit_links(datas)
    elif choice.strip() == '0':
        print("[CANCELLED]")
    else:
        _confirm_upload(datas)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, default=5)
    parser.add_argument('--grouped', '-g', action='store_true', help='Enable grouping products')
    args = parser.parse_args()
    count = args.count
    additional_count = 2 if args.grouped else 0
    datas = _get_random_entries(count, additional_count)

    if len(datas) <= 0:
        print('No available data. Run collect.py to get more data.')
    else:
        _confirm_data(datas)


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
