import argparse
import os
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd
from pandas.core.groupby import DataFrameGroupBy

from __table import C_IS_UPLOADED, C_STOCK, C_TIKTOK_V, C_SHOP_ID


def delete_file(file: str):
    if os.path.exists(file):
        os.remove(file)


def save_csv(file_path: str, data: dict, duplicate_subset: list):
    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
    else:
        existing_df = pd.DataFrame()

    print(f'Existing {len(existing_df)} rows')
    new_df = pd.DataFrame(data)
    print(f'Add new {len(new_df)} rows')
    merged_df = pd.concat([existing_df, new_df])
    print(f'Merged become: {len(merged_df)} rows')
    final_df = merged_df.drop_duplicates(subset=duplicate_subset).reset_index(drop=True)
    print(f'Final distinct: {len(final_df)} rows')
    final_df.to_csv(file_path, index=False)


def _reset_all_uploaded_to_false(usr: str):
    print('!!! This should not be used in production !!!')
    df_file = f'data/scrap/products_{usr}.csv'
    try:
        if Path(df_file).exists():
            df = pd.read_csv(df_file)
            df[C_IS_UPLOADED] = False
            df.to_csv(df_file, index=False)
            print(df[C_IS_UPLOADED])

    except FileNotFoundError:
        pass


def _clear_remote_files():
    print("Clear Remote")
    tiktok_dir = '/sdcard/_tiktok_videos'
    affiliate_dir = '/sdcard/_shop-affiliate-videos'
    try:
        os.system(f"adb shell 'cd {tiktok_dir} && rm -rf *'")
        os.system(f"adb shell 'cd {affiliate_dir} && rm -rf *'")
        print('Remote videos cleared')
    except Exception as e:
        print(e)


def _default():
    return "Function not found"


def set_entry_uploaded(video_url: str, usr: str) -> bool:
    try:
        df_file = f'data/scrap/tiktoks_{usr}.csv'
        if Path(df_file).exists():
            df = pd.read_csv(df_file)

            index = df.loc[df[C_TIKTOK_V] == video_url].index[0]
            df.loc[index, C_IS_UPLOADED] = True
            df.to_csv(df_file, index=False)
            print(f'[{index + 2}] is uploaded (True)')
            return True

    except FileNotFoundError:
        pass
        return False


def get_datas(usr: str, count: int = 1) -> DataFrameGroupBy:
    product_file = f'data/scrap/products_{usr}.csv'
    tiktok_file = f'data/scrap/tiktoks_{usr}.csv'
    if Path(product_file).exists() and Path(tiktok_file).exists():
        p_df = pd.read_csv(product_file)
        t_df = pd.read_csv(tiktok_file)
        filtered_tiktok = t_df[t_df[C_IS_UPLOADED] == False]
        random_tiktok = filtered_tiktok.sample(n=count, replace=True) if count <= len(filtered_tiktok) else t_df
        result_df = pd.DataFrame()
        for _, row in random_tiktok.iterrows():
            shop_id = int(urlparse(row['link']).path.split('/')[2])
            selected_rows = p_df[p_df[C_SHOP_ID] == shop_id].sample(n=6, replace=True)
            selected_rows[C_TIKTOK_V] = [row[C_TIKTOK_V]] * len(selected_rows)
            result_df = pd.concat([result_df, selected_rows])
        grouped_result = result_df.groupby(C_TIKTOK_V)
        return grouped_result


def get_grouped_datas(usr: str, group_by: str, count: int = 1) -> DataFrameGroupBy:
    df_file = f'data/scrap/products_{usr}.csv'
    if Path(df_file).exists():
        df = pd.read_csv(df_file)
        # get uploaded False and stock > 1
        filtered = df[(df[C_IS_UPLOADED] == False) & (df[C_STOCK] > 1)]
        # only take group that has > 2 rows
        filtered_len = filtered.groupby(df[group_by]).filter(lambda x: len(x) > 2)
        grouped = filtered_len.groupby(df[group_by])

        # Limit Group by Request
        if 0 < count < len(grouped):
            group_limit = min(count, len(grouped))
            random_names = np.random.choice(list(grouped.groups.keys()), group_limit, replace=False)
            selected_groups = [grouped.get_group(group_name) for group_name in random_names]
            return pd.concat(selected_groups).groupby(df[group_by])
        else:
            return grouped


def choose_action(function_name, usr: str):
    switch_func = {
        'reset_uploaded': _reset_all_uploaded_to_false,
        'clear_remote': _clear_remote_files,
        'none': _default
    }
    selected = switch_func.get(function_name, _default)
    return selected(usr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('function', help='''
            To call function inside util, use below options:
            "reset_uploaded" to reset all products as unpublished
            "clear_remote" to delete all video files in remote devices (via adb)
            ''', type=str)
    parser.add_argument('username')
    args = parser.parse_args()
    choose_action(args.function, args.username)
