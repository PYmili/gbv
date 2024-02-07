import os
import argparse
from typing import Union

from loguru import logger

from methods import get_ffmpeg_hwaccels


INPUT = ["--url", "-i"]
OUTPUT = ["--output", "-o"]
BROWSER = {"edge": 0, "chrome": 1, "firefox": 2}
HWACCELS = get_ffmpeg_hwaccels()


def terminal() -> Union[dict, None]:
    # 创建ArgumentParser对象
    parser = argparse.ArgumentParser(description="\"Get Bilibili Video\"(GBV) Program.")

    # 添加命令行参数及其相应的值
    parser.add_argument("--url", "-i", dest="link", type=str, required=True, 
                        help="提供要抓取的链接，可以是收藏夹，单个视频链接。（必选）")
    parser.add_argument("--output", "-o", dest="save_path", type=str, required=False, 
                        help="提供要保存的路径。（默认当前目录）")
    parser.add_argument("--browser", "-b", dest="browser", type=str, required=False,
                        help=f"获取cookies时指定浏览器，\"{', '.join(BROWSER.keys())}\"（默认edge）")
    parser.add_argument("--cache", "-c", dest="cache", type=str, required=False,
                        help="缓存，可将cookies缓存，用于下次使用。（选填）")
    parser.add_argument("--page", "-p", dest="page", type=int, required=False,
                        help="缓存视频的页数，暂时只可对合集视频进行页数缓存。（默认全部缓存）")
    parser.add_argument("--hwaccels", dest="hwaccels", required=False, default=False,
                        help=f"给ffmpeg添加硬件加速，此处查询到您可用的加速硬件有：{', '.join(HWACCELS)}。（选填）")
    parser.add_argument("--libx264", "--windows", dest="libx264", required=False, default=False, action='store_true',
                        help="将视频编码转换为h.264编码，用来适配windows平台。（默认关闭）")

    # 解析命令行参数
    args = parser.parse_args()
    
    reuslt = {
        "output": os.getcwd(),
        "browser": BROWSER["edge"],
        "cache": False,
        "page": 0,
        "hwaccels": False,
        "libx264": False
    }

    if args.link:
        reuslt["input"] = args.link
    if args.save_path:
        reuslt["output"] = args.save_path
    if args.browser and args.browser in BROWSER.keys():
        reuslt["browser"] = BROWSER[args.browser]
    if args.cache:
        reuslt["cache"] = args.cache
    if args.page:
        reuslt["page"] = args.page
    if args.hwaccels and HWACCELS:
        if args.hwaccels in HWACCELS:
            reuslt["hwaccels"] = args.hwaccels
        else:
            logger.warning("未检测到此硬件，将不设置硬件加速。")
    if args.libx264:
        reuslt["libx264"] = True

    return reuslt


if __name__ in "__main__":
    terminal()