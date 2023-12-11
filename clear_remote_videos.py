import os


def main():
    remote_dir = '/sdcard/_affiliate_videos'
    try:
        os.system(f'adb shell rm -r {remote_dir}')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
