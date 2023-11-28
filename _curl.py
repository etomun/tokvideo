import json
import subprocess


def set_fav_product(is_fav: bool, shop_id: str, product_id: str) -> bool:
    endpoint = 'like_items' if is_fav else 'unlike_items'

    curl_command = [
        'curl',
        '-X', 'POST',
        f'https://shopee.co.id/api/v4/pages/{endpoint}',
        '-H', 'Authorization: Bearer YOUR_ACCESS_TOKEN',
        '-H', 'Content-Type: application/json',  # Specify the content type
        '-H', 'authority: shopee.co.id',
        '-H', 'accept: application/json',
        '-H', 'accept-language: en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7,id;q=0.6',
        '-H', 'content-type: application/json',
        '-H', 'if-none-match-: 55b03-857d315c55a0e852d6496d6bda3a0df7',
        '-H', 'origin: https://shopee.co.id',
        '-H',
        'referer: https://shopee.co.id/Giza-Grill-Pan-Cast-Iron-i.380376784.13556893601??publish_id=&sp_atk=458a3860-515d-44dc-89b9-00dd59ec75f3&xptdk=458a3860-515d-44dc-89b9-00dd59ec75f3',
        '-H', 'sec-ch-ua: "Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        '-H', 'sec-ch-ua-mobile: ?0',
        '-H', 'sec-ch-ua-platform: "macOS"',
        '-H', 'sec-fetch-dest: empty',
        '-H', 'sec-fetch-mode: cors',
        '-H', 'sec-fetch-site: same-origin',
        '-H',
        'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        '-H', 'x-api-source: pc',
        '-H', 'x-csrftoken: bZ4aC5e1qrOzU0NJIHKgP7Xmpfm3Egg8',
        '-H', 'x-requested-with: XMLHttpRequest',
        '-H', 'x-sap-ri: 3c16666532d58550f530fa3d01013c7d7ab09859c163a8403bf3',
        '-H',
        'x-sap-sec: j8403gWC5uOYIuOYJpOiIuBYJpOYIuBYIuOaIuOYNusYIqfCIur7IwOYJuOYIWj5wQxiIuOYmuIYIWfwIukJNcXsyfUsoe7OKsuhMEOkUp+oiuFlRebxXnmPO86qf9zzOUqmOuruJzG7PKhPLeBV4KRFrRHm70PsqQ35JTYkkI6po10dO5s1nIsuPQkZTovZiFV28adPayqE/LCFcR0yQWJ+ohg0HD8y02GoVZjXdn7xfymgENQQ/4R0x16NAwlKtNeAqHBB/qpYiii8FHbZLvwSZlUXVolQZW7CyFQqNXdz4i8/7cRVtBequvB2cYs2JwDxBDvczQNF1jqeQ3pp1t0uXwSR5vMKmYRE40c+pdwojWHTGsU51+D83fqjDewPcXyDPRvsbhPtJJm0xpJ9hXulFZ3oMm8r+/VQKGy5JhmWXnoTh7oe3E+zp+5MY4RfY20/8Rde7bCMxFs7+AjKzNBCiFRrML0RQOMPq6INN/NcYc69ci406knsaV8fSxtnXsb3V35MkUMGNsUUyb2ozgMWkIvUk7s20v6gDogvlrMIsb16bWlDKxqdHAayZkWEk4bS+5BeMrdP8sAQvloDIoSCY4pxPm8gzdiiwNBgsBkhxcOM5MGjVu4zHk7NdhuTCVarPbBFHZAjjTWs6zrJ6XaTa1EEhpMpCNCiIuOYhsP/seeL3nKYIuOY9DbJw2WYIuOTIuOYPuOYIvi6U/yPlh47P2Yy3ELSf6i56yoU4uOYIn/kssEhsUEsIuOYIAjJwQxiIuOYruOYIqBYIukSfAoXdHME3tHUDmLX3giOPvhFopWYIuP6/eKs/sBhowOYIuOiIufY4uOaIuWYIuOiIuOYruOYIqBYIukSd3xq+o9K2Q9n3Q1Ebx1waO2zBwWYIuOp/CsesnBHowOYIuO=',
        '-H', 'x-shopee-language: en',
        '--compressed',
        '-b',
        '__LOCALE__null=ID; csrftoken=bZ4aC5e1qrOzU0NJIHKgP7Xmpfm3Egg8; _fbp=fb.2.1671691525641.722325261; _tt_enable_cookie=1; _ttp=HA3wQHY3B2CtgbRVrph8LTlSuAo; _QPWSDCXHZQA=171a5039-0119-41eb-fceb-fc2fe0164fde; _fbc=fb.2.1672629331899.IwAR1LPjC1cr3R5AlQzkRBhMKQvQ4hjr6bNrmQT8tY9HRqCOT91qCa9N0LmCk; SPC_CLIENTID=UmFmV1U0N2x3YmxGvymyjxlcqjtzndzs; SPC_IA=1; __stripe_mid=938c8899-a191-4af3-b9c3-6cdbca6f4a7eba1d10; language=en; SPC_F=PotThYhfyczry0d8dc4LABk1KI85fFUV; REC_T_ID=d8b5a598-4deb-11ee-809f-f4ee08261793; _gcl_au=1.1.624132024.1696216583; _gcl_aw=GCL.1696906138.CjwKCAjwyY6pBhA9EiwAMzmfwRK__bb04KI6gb_9PJTZIwcow5Fvu_cwa_Li4bgGyxh1rmZYpD-qvBoCeG4QAvD_BwE; _gac_UA-61904553-8=1.1696906139.CjwKCAjwyY6pBhA9EiwAMzmfwRK__bb04KI6gb_9PJTZIwcow5Fvu_cwa_Li4bgGyxh1rmZYpD-qvBoCeG4QAvD_BwE; _ga_8TJ45E514C=GS1.1.1698424089.4.1.1698424729.60.0.0; SC_DFP=mXXvwSbOxnItOxaqBkCkvGiQMaDEXwbk; SPC_SC_SA_TK=; SPC_SC_SA_UD=; _ga_QMX630BLLS=GS1.1.1699091017.3.1.1699091939.60.0.0; _med=affiliates; SPC_ST=.S2h0QjlBbEVJdEZoWGJET1yhShQdQj3KRNdGEIDjjNiBUWtzTF502arAYQ25YJ3f80qhYNEyrypPBkbyQkfHVPiSNrxQJNkovnE3GVbAfFprd93Pj873s3gzriUZO0fS3Ul3UIJocA+pKAAIFwj8epIZgUq9rv9/K19dVOBoQ5/TXDQxvcm0HX7IThV0ekunernFJCaMHLmZltq9C1aADw==; SPC_U=1098761675; SPC_R_T_ID=yC3R75SUEYIK7szB6p1nZbeyWmXNNZR+Kq31yURCCnru7p7tKK3Ft1VBbdGQ3NO1nqxM8HNyG0V7cfEYCraMkanYJaNgnmgeTijkZGudQE6SRo9VhYMd6Pj79oP31gYN6Z3phVeCWFfA50gmk5bqsbeEXKelEGQOjWlDeU7BBzg=; SPC_R_T_IV=eVFRamJkRHNXQkhGYkdHaw==; SPC_T_ID=yC3R75SUEYIK7szB6p1nZbeyWmXNNZR+Kq31yURCCnru7p7tKK3Ft1VBbdGQ3NO1nqxM8HNyG0V7cfEYCraMkanYJaNgnmgeTijkZGudQE6SRo9VhYMd6Pj79oP31gYN6Z3phVeCWFfA50gmk5bqsbeEXKelEGQOjWlDeU7BBzg=; SPC_T_IV=eVFRamJkRHNXQkhGYkdHaw==; SPC_SEC_SI=v1-eEU5NjlneTdqQnBSV3dLRhVURITtASHIsOtaMKYJEt+YsHtFrAmGZCgEdH2jE4gY6G3dkBToljNnUq0jRJeoyHQkRX2IBXZHzRKpL+NMXfw=; SPC_SI=c7VlZQAAAAB2ZE1lTncwNU2SCAAAAAAAd0ZwNDNvb2c=; _sapid=fa8af575-4dfb-400e-8211-1ed4bf735d2a; REC7iLP4Q=a477373d-daa9-4384-b48e-c4ead5b2ec13; _gid=GA1.3.1842883207.1701185530; _ga_SW6D8G0HXK=GS1.1.1701185529.121.1.1701188945.58.0.0; _ga=GA1.1.2066265449.1671691526; shopee_webUnique_ccd=I%2FgFiggVTASMaetwVq%2BqIA%3D%3D%7CGqJmgPAPVFgCJ9m2SO5MlNIQHQM2G7KRnV5oZjdROgtJhRGTPMKbpY6kM6udqmWef5yI4XJQcAVwGQ%3D%3D%7CcmFoXeD6nLTfpDCs%7C08%7C3; ds=2a98eb5829f7c1e3186af2ddad98304e; SPC_EC=dkxhVnZVeW44OEc2SzVuZQPso0UcCZgly6C/HYoOkcELA5NBD8T+6cg1byXQOItNVL0oveIYWVFeN+01IWQ95fCHLVSXbQ9iXGZkt8isj8N/QKSaU6Fzpo1C14+wHnc45/+MtqqhgIgfeKJNCWNGA+62gVuszr2bujE5WwPhM6Y=',
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
