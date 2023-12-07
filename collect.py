import argparse
import concurrent.futures.thread
import os
import re
from argparse import Namespace
from pathlib import Path

import pandas as pd
import requests

from __api import affiliate_cookies, affiliate_headers, affiliate_base_url
from __table import *
from _tiktok import get_tiktok_url


def __get_args() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", "-k", help="White space not accepted, replace with -. Separate keys with ,",
                        type=str, default="")
    parser.add_argument("--limit", "-l", help="limit the offers results", type=int, default=50)
    parser.add_argument("--headed", "-ht", action="store_true", help="Enable headed tiktok for captcha", default=False)
    return parser.parse_args()


def __filter_product(p: dict) -> bool:
    name = p['batch_item_for_item_card_full']['name']
    price = __int(p['batch_item_for_item_card_full']['price'])
    stock = p['batch_item_for_item_card_full']['stock']

    filter_rate = __int(p['seller_commission_rate']) + __int(p['default_commission_rate']) >= 10
    filter_rating = p['batch_item_for_item_card_full']['shop_rating'] >= 4.5
    filter_selling = p['batch_item_for_item_card_full']['historical_sold'] >= 30
    filter_stock = stock >= 100 if price < 10000 * 100000 else stock >= 10

    result = filter_rate & filter_rating & filter_selling & filter_stock
    if not result:
        print(f'Filtered {name}')
    if not filter_rate:
        print(f'Commission under 10%')
    if not filter_rating:
        print(f'Rating under 4.5')
    if not filter_selling:
        print(f'Selling under 30 items')
    if not filter_stock:
        print(f'Out of stock')

    return result


def __clean_title(product: dict) -> str:
    title = product['batch_item_for_item_card_full']['name']
    return re.sub('[^A-Za-z0-9 ]+', '', title)


def __get_shop_video(product: dict) -> str:
    videos = product['batch_item_for_item_card_full']['video_info_list']
    return '' if len(videos) <= 0 else videos[0]['default_format']['url']


def __generate_tit_kok_keywords(shop_name: str, product_title: str) -> str:
    s_1st_word = ' '.join(shop_name.split()[:1])
    t_1st_word = ' '.join(product_title.split()[:1])
    t_first_7 = ' '.join(product_title.split()[:7])
    return t_first_7 if s_1st_word.lower() == t_1st_word.lower() else s_1st_word + ' ' + t_first_7


def __int(str_val: str) -> int:
    return int(re.sub(r"\D", "", str_val))


def __parse_response(filtered_products: list, keyword: str = "") -> dict:
    filtered_count = len(filtered_products)

    product_ids = list(map(lambda p: p['item_id'], filtered_products))
    titles = list(map(__clean_title, filtered_products))
    shop_ids = list(map(lambda p: p['batch_item_for_item_card_full']['shopid'], filtered_products))
    shop_names = list(map(lambda p: p['batch_item_for_item_card_full']['shop_name'], filtered_products))
    links = list(map(lambda p: p['product_link'], filtered_products))
    seller_rates = list(map(lambda p: __int(p['seller_commission_rate']), filtered_products))
    default_rates = list(map(lambda p: __int(p['default_commission_rate']), filtered_products))
    total_rates = [s + d for s, d in zip(seller_rates, default_rates)]
    images = list(map(lambda p: p['batch_item_for_item_card_full']['image'], filtered_products))
    videos = list(map(__get_shop_video, filtered_products))
    stocks = list(map(lambda p: p['batch_item_for_item_card_full']['stock'], filtered_products))
    ratings = list(map(lambda p: p['batch_item_for_item_card_full']['shop_rating'], filtered_products))
    prices = list(map(lambda p: __int(p['batch_item_for_item_card_full']['price']) / 100000, filtered_products))
    is_officials = list(map(lambda p: p['batch_item_for_item_card_full']['is_official_shop'], filtered_products))
    est_commissions = [r * p * 0.01 for r, p in zip(seller_rates, prices)]
    keywords = [keyword] * filtered_count
    is_uploads = [False] * filtered_count

    tiktok_keywords = list(map(__generate_tit_kok_keywords, shop_names, titles))
    print(f'\nGet Tiktok video for {len(tiktok_keywords)} items')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tiktok_videos = list(executor.map(lambda x: get_tiktok_url(x, not args.headed), tiktok_keywords))
    data = {
        C_IS_UPLOADED: is_uploads,
        C_KEYWORD: keywords,
        C_TIKTOK_K: tiktok_keywords,
        C_LINK: links,
        C_TIKTOK_V: tiktok_videos,
        C_VIDEO: videos,
        C_TITLE: titles,
        C_SHOP_NAME: shop_names,
        C_STOCK: stocks,
        C_EST_COMM: est_commissions,
        C_PRICE: prices,
        C_TOTAL_RATE: total_rates,
        C_SELLER_RATE: seller_rates,
        C_DEFAULT_RATE: default_rates,
        C_RATING: ratings,
        C_IMAGE: images,
        C_SHOP_ID: shop_ids,
        C_ID: product_ids,
        C_IS_OFFICIAL: is_officials
    }

    return data


def get_limits(total_limit):
    limits = []
    while total_limit >= 50:
        limits.append(50)
        total_limit -= 50
    if total_limit > 0:
        limits.append(total_limit)
    return limits if len(limits) > 0 else [0]


def __search_products(keyword_limit: dict) -> dict:
    keyword = keyword_limit['keyword']
    limit = keyword_limit['limit']
    print(f"Searching for {keyword}")

    products = []
    for i, page_limit in enumerate(get_limits(limit)):
        page_offset = i * 50
        url = f"{affiliate_base_url}/offer/product/list"
        # sort by commission
        # filter by Extra Commission
        querystring = {"keyword": keyword, "list_type": 0, "match_type": 1, "sort_type": 5, "page_offset": page_offset,
                       "page_limit": page_limit, "client_type": 1, "filter_types": 2, "filter_shop_types": 1}
        response = requests.request("GET", url, cookies=affiliate_cookies, headers=affiliate_headers,
                                    params=querystring).json()
        try:
            datas = response['data']['list']
            print(f'Response {keyword} Page {i + 1}: {len(datas)}')
            products += datas
        except Exception as e:
            print(f'Error {keyword}: Page {i + 1}')
            print(e)
            break

    print(f'Total Products: {len(products)}\n')
    if len(products) <= 0:
        print('Get 0 Result\n')
        exit(1)

    filtered_products = list(filter(__filter_product, products))
    if len(filtered_products) <= 0:
        print("No data match the filters")
        return {}
    else:
        print(f"Retrieved {len(filtered_products)} items for {keyword}")
        final_products = filtered_products[:1] if args.headed else filtered_products
        return __parse_response(final_products, keyword)


# noinspection PyUnresolvedReferences
def __save_csv(data: dict):
    base_dir = "data/scrap"
    full_path = base_dir + "/products.csv"
    os.makedirs(base_dir, exist_ok=True)

    df = pd.DataFrame.from_dict(data)
    try:
        if Path(full_path).exists():
            existing = pd.read_csv(full_path)
            if not existing.empty:
                df = pd.concat([existing, df]).drop_duplicates(keep=False)
    except FileNotFoundError:
        pass
    finally:
        df = df.dropna(subset=[C_TIKTOK_V])
        df.to_csv(full_path, index=False)
        print(f'Current Entries: {len(df.index)} items')


def search(keywords: list, limit: int):
    if all(s == '' for s in keywords):
        single_result = __search_products({'keyword': '', 'limit': limit})
        __save_csv(single_result)

    else:
        keywords_n_limits = list(map(lambda q: dict({'keyword': q, 'limit': limit}), keywords))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(__search_products, keywords_n_limits))

        merged = {}
        for d in results:
            for k in d:
                if k not in merged:
                    merged[k] = []
                merged[k].extend(d[k])
        __save_csv(merged)


def main():
    s_keywords = args.keywords
    i_limit = args.limit
    parsed_keys = s_keywords.replace('-', ' ')
    keys: list = parsed_keys.split(',')
    search(keys, i_limit)


if __name__ == '__main__':
    args = __get_args()
    proxy_ip = '109.92.133.194:5678'
    proxies = {
        'http': f'http://{proxy_ip}',
        'https': f'https://{proxy_ip}'
    }
    session = requests.Session()
    # session.proxies = proxies
    main()
