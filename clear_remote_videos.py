import os


def main():
    tiktok_dir = '/sdcard/_tiktok_videos'
    affiliate_dir = '/sdcard/_shop-affiliate-videos'
    try:
        os.system(f'adb shell rm -r {tiktok_dir}')
        os.system(f'adb shell rm -r {affiliate_dir}')
        print('Remote videos cleared')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
