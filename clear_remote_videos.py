import os


def main():
    tiktok_dir = '/sdcard/_affiliate_videos'
    try:
        os.system(f'adb shell rm -r {tiktok_dir}')
        print('Remote videos cleared')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
