import os


def clear_tiktok_dir() -> bool:
    tiktok_dir = '/sdcard/_tiktok_videos'
    try:
        os.system(f"adb shell 'cd {tiktok_dir} && rm -rf *'")
        os.system(f"adb shell \"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{tiktok_dir}\"")
        return True
    except Exception as e:
        print(e)
        return False


def clear_affiliate_dir() -> bool:
    vid_dir = '/sdcard/_shop-affiliate-videos'
    try:
        os.system(f"adb shell 'cd {vid_dir} && rm -rf *'")
        os.system(f"adb shell \"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{vid_dir}\"")
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    print(clear_tiktok_dir())
