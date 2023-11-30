import json
import subprocess


def set_fav_product(is_fav: bool, shop_id: str, product_id: str) -> bool:
    endpoint = 'like_items' if is_fav else 'unlike_items'

    curl_command = [
        'curl',
        '-X', 'POST',
        f'https://shopee.co.id/api/v4/pages/{endpoint}',
        '-H', 'authority: shopee.co.id',
        '-H', 'accept: application/json',
        '-H', 'content-type: application/json',
        '-H', 'if-none-match-: 55b03-857d315c55a0e852d6496d6bda3a0df7',
        '-H', 'origin: https://shopee.co.id',
        '-H', 'referer: https://shopee.co.id/Giza-Grill-Pan-Cast-Iron-i.380376784.13556893601??publish_id=&sp_atk=458a3860-515d-44dc-89b9-00dd59ec75f3&xptdk=458a3860-515d-44dc-89b9-00dd59ec75f3',
        '-H', 'sec-ch-ua: "Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        '-H', 'sec-ch-ua-mobile: ?0',
        '-H', 'sec-ch-ua-platform: "Windows"',
        '-H', 'sec-fetch-dest: empty',
        '-H', 'sec-fetch-mode: cors',
        '-H', 'sec-fetch-site: same-origin',
        '-H', 'user-agent: ',
        '-H', 'x-api-source: pc',
        '-H', 'x-csrftoken: bZ4aC5e1qrOzU0NJIHKgP7Xmpfm3Egg8',
        '-H', 'x-requested-with: XMLHttpRequest',
        '-H', 'x-sap-ri: 3c16666532d58550f530fa3d01013c7d7ab09859c163a8403bf3',
        '-H', 'x-sap-sec: ',
        '-H', 'x-shopee-language: en',
        '--compressed',
        '-b', '',
        '-d', f'{{"shop_item_ids":[{{"shop_id":{shop_id},"item_id":{product_id}}}]}}'
    ]

    try:
        process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Check if successful (exit code 0)
        if process.returncode == 0:
            response_json = json.loads(stdout.decode('utf-8'))
            print(response_json)
            return response_json['error'] == 0

        else:
            print(f"Error running cURL command. stderr: {stderr.decode('utf-8')}")
            return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


if __name__ == '__main__':
    set_fav_product(False, '8459024', '2058513456')
