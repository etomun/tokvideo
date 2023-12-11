import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.core.groupby import DataFrameGroupBy

from __table import C_IS_UPLOADED, C_STOCK, C_TIKTOK_V


def delete_file(file: str):
    if os.path.exists(file):
        os.remove(file)


def save_products(data: dict, usr: str):
    size_before = 0
    base_dir = "data/scrap"
    full_path = f"{base_dir}/products_{usr}.csv"
    os.makedirs(base_dir, exist_ok=True)
    df = pd.DataFrame.from_dict(data)
    print(f'New dataframe: {len(df)}')
    try:
        if Path(full_path).exists():
            existing = pd.read_csv(full_path)
            size_before = len(existing)
            if not existing.empty:
                df = pd.concat([existing, df])
        print(f'After concat dataframe: {len(df)}')
        df = df.dropna(subset=[C_TIKTOK_V])
        print(f'After drop empty Tiktok dataframe: {len(df)}')
        df = df.drop_duplicates()
        print(f'Final dataframe: {len(df)}')
    except Exception as e:
        print(e)
        pass
    finally:
        df.to_csv(full_path, index=False)
        addition = len(df) - size_before
        print(f'Products Added: {addition} items.\nCurrent Entries: {len(df.index)} items')


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


def set_entry_uploaded(index: int, usr: str) -> bool:
    try:
        df_file = f'data/scrap/products_{usr}.csv'
        if Path(df_file).exists():
            df = pd.read_csv(df_file)
            df.loc[index, C_IS_UPLOADED] = True
            df.to_csv(df_file, index=False)
            print(f'[{index + 2}] is uploaded (True)')
            return True

    except FileNotFoundError:
        pass
        return False


def get_single_datas(usr: str, group_by: str, count: int = 1) -> DataFrameGroupBy:
    df_file = f'data/scrap/products_{usr}.csv'
    if Path(df_file).exists():
        df = pd.read_csv(df_file)
        filtered = df[(df[C_IS_UPLOADED] == False) & (df[C_STOCK] > 1)]
        random_1 = filtered.sample(n=count, replace=True) if count <= len(filtered) else df
        return random_1.groupby(df[group_by])


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
