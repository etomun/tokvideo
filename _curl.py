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
        '-H', 'accept-language: en-US,en;q=0.9',
        '-H', 'content-type: application/json',
        '-H', 'if-none-match-: 55b03-7c12ef5677e5f56ef0eb7b7addc4015a',
        '-H', 'origin: https://shopee.co.id',
        '-H', 'priority: u=1, i',
        '-H', 'referer: https://shopee.co.id',
        '-H', 'sec-ch-ua: "Chromium";v="121", "Not A(Brand";v="99"',
        '-H', 'sec-ch-ua-mobile: ?0',
        '-H', 'sec-ch-ua-platform: "macOS"',
        '-H', 'sec-fetch-dest: empty',
        '-H', 'sec-fetch-mode: cors',
        '-H', 'sec-fetch-site: same-origin',
        '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        '-H', 'x-api-source: pc',
        '-H', 'x-csrftoken: jmswc1D2pHn07KAifcGmqbzVkUkqywxR',
        '-H', 'x-requested-with: XMLHttpRequest',
        '-H', 'x-sap-ri: a50a6765309eb10bb2edb33e0101fd3c482c46c1a5ffea72debe',
        '-H',
        'x-sap-sec: RXwMZMsY5psCIpsCJusfIpKCJusCIpKCIpsxIpsCMpOCIoKYIppDI2sCJpsCI52JwllfIpsCupECIOKGIpoRaeV0xOr426qpwvaV8QhxGO3UnYtX8sqVsQO9ao06pcljcKjND3wnlF01ha4/C05xMZC9I+ArODaKSxfmMxTmh0XL07MUmjO1WGpqiGhe6GXfmPpVkuPYlXh+a4hcrf1iYEWdeex7vXirLeQYMOw15mYN4rrXE9aPXeN34Z1+Uy9Pig+FuTJPO7zbCHh8vw3lxeZs3RXgZL8a4euwl4S58sOOt0pyfeejgYAhPBaVRFbscKkgRBFr4srZjA7kZvtp7Pptk/pqx2pvDnaByXGL1cLxeefrZNzEqDR/E6AcIZ3CiX1rvloIehIoxzXDx2+FBrUtAH/oSQWY9e+x/sXsgU7ODXnBMoY6iwfGvBrPZNkmYrEinZOdDEkGSPNzy9gbI19qwRWKRT8RoeQXmTce/u6Lv2nACojYXi0ZvqtMmFU/hZJxMmBTz9NBCm29lCEEITH06pWry7yx9pYFhRMdDTbo2/uVqF1fp092xBFNF0Af6C1tdHFNQoPYK3yEbaNDhXeL2og5GAvhyguBXsxNlH/PN4f7ghv1IUUF63rdJO8AvRqtwEPSHUIGAYq1U2mZ/4SL4psCIee3/ZJ/hnQHIpsCIku5wllfIpsCrpsCIoKCIpo9mupwbGNc9S0EriO6UDNE9C+1/pnCIph2sKssss37hpsCIpplwlz54psCIoCCIpsvIpsCSig1f+sBUiDmMyfeb6qPniV4kExfIpsC/KvEsnve3eKCIpsC4pslIpnCJpsfIpsC4psCIoCCIpsvIpsCj+yePClgFyf0RuWDzEtmwSFGj3nfIpsCh3IoseM//CKCIpsC',
        '-H', 'x-shopee-language: id',
        '-d', f'{{"shop_item_ids":[{{"shop_id":{shop_id},"item_id":{product_id}}}]}}',
        '-b', '_gcl_au=1.1.150722862.1700901294; _fbp=fb.2.1700901294684.358010378; SPC_F=b87Wrgq5ZOlkxtojWjhwWB9MzHtJMG6w; REC_T_ID=849b8f49-8b6d-11ee-9390-9a54c8c7bb98; SPC_CLIENTID=Yjg3V3JncTVaT2xrufrcgabcjzxpljla; SPC_ST=.dmxMOGU5dTdBTkVVNURSVjXUO7sikdLg5GlIN9kIwO7uMT4YiCcRY0kphmuD5fm3pa1FSiYaIIKkRWC40L7fNW+mCmBtyu1xNf5iLj4rvx/aa9vjmQfdmh8gi+ouOw0nTbvih+/IIYpy0YYz6i3yU5YH5kykbLeLNrDPWas5/EphHf+d2Ud4Huf0Ik6oW9uGSl0zy8b3mH+IqsV7FBAr8g==; SPC_U=1098761675; SPC_R_T_ID=ihXcYx2zPRsM87FmDR9SjbXsc4aO/EmAPUJg91XAgwwZb56sDJO+Xu6G8IAoIlFJYrwZgXDyi/id5XZW+zmDqQIqLHo0U9oqk4kYIMqfevOe4nKozwnHCoaHB6FPxH9hW3NzIYpqgQ1mNCqm/Jx+9brc/PrehfXwI21EOI3yfP4=; SPC_R_T_IV=UE12SjlkM09iS3ZxcllFeA==; SPC_T_ID=ihXcYx2zPRsM87FmDR9SjbXsc4aO/EmAPUJg91XAgwwZb56sDJO+Xu6G8IAoIlFJYrwZgXDyi/id5XZW+zmDqQIqLHo0U9oqk4kYIMqfevOe4nKozwnHCoaHB6FPxH9hW3NzIYpqgQ1mNCqm/Jx+9brc/PrehfXwI21EOI3yfP4=; SPC_T_IV=UE12SjlkM09iS3ZxcllFeA==; SPC_SI=cLVlZQAAAAA3UFVpVEowULtuCgAAAAAAd2dvaU9QUm8=; SPC_SEC_SI=v1-MDRZbG1TNlJ6elRhdU9uUVHPrGoGVwFniMZ/eVqzW7+AQUpcoRRcJg6HWgnM4ep9JA8bYpzWP/q45YBoixUjVf5gn2Q1XBUnnbImy+iSZfA=; _gid=GA1.3.2056757509.1701183483; csrftoken=jmswc1D2pHn07KAifcGmqbzVkUkqywxR; _sapid=0bc9dfcb-10bb-41da-9279-3949d9645a99; _QPWSDCXHZQA=358260c5-8901-4575-bee0-3cdcefed8574; REC7iLP4Q=db900f77-6e28-4f22-81ad-de6b6e0a5590; AMP_TOKEN=%24NOT_FOUND; SPC_IA=1; _ga_SW6D8G0HXK=GS1.1.1701251685.9.1.1701251733.12.0.0; _ga=GA1.3.487855131.1700901295; shopee_webUnique_ccd=csitwOqXnjtnxpMEYNZefA%3D%3D%7CMcJHCuqhWH3YWnUdp%2Fn3x6hPAOPG%2Bbt6KbaGUOGmQxNvAua0svm2ktJ%2FPe8Ph3P%2B7p%2BASAYzqfU%3D%7CJJDmdMmZIFPbwSaB%7C08%7C3; ds=5cafc55c4e5d66e03695d4f631b0d7f1; SPC_EC=RmdNSU5hQ0ZsTkswUENjQsJpBP9NQKRSi5IIAxjcoY5zeJDWclx6QWipvj/e6TJsW8WPB9qZbkOECLBAWmty7WOkTlvYscMsZ2el8OnEijQa+S5kVUTmylGYjoaEjTA7q0BInDwhDtqHTgTg9h95Dj/tkgbvkgo3zHLknJMSpyM=',
        '--compressed'
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
