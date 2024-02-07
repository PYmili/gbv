import os
import time
from typing import Union

from loguru import logger

from GetBilibiliVideo import GBV
from terminal import terminal


def starter(
        url: str,
        browser: int,
        outputDir: str = os.getcwd(),
        page: int = 0,
        cookies: Union[str, bool] = False,
        IfStartCache: bool = False,
        hwaccels: Union[str, False] = False,
        libx264: bool = False
) -> GBV:
    """
    启动器 启动GBV类

    :param cookies: 自定义cookies值
    :param page: 要下载的页数
    :param outputDir: 输出路径
    :param url: 要访问的 URL 地址
    :param browser: 选择要获取 cookies 的浏览器
    :param IfStartCache: 是否开启Cookie缓存
    :param hwaccels: 给ffmpeg添加硬件加速
    :param libx264: 是否转换为h.264编码
    :return: None
    """
    # 生成向服务器请求的params 值
    splitValue = url.split("video")[-1]
    splitValue = splitValue.split("/", 1)[-1].split("/", 1)
    params = {
        "bvid": splitValue[0]
    }
    # 如果url链接中存在参数，就将其记录下来
    if splitValue[-1]:
        for i in splitValue[-1][1:].split("&"):
            try:
                key, value = i.split("=")
            except ValueError:
                continue
            try:
                params[key] = eval(value)
            except Exception:
                params[key] = value

    # 生成传入函数的 args 值
    args = {}
    if page != 0:
        args['page'] = [i for i in range(page)]
    else:
        # 下载全部页
        args["page"] = 0

    gbv = GBV(
        url=url,
        browser=browser,
        params=params,
        outputDir=outputDir,
        args=args,
        cookies=cookies,
        IfStartCache=IfStartCache,
        hwaccels=hwaccels,
        libx264=libx264
    )
    logger.add(f"log/latest.log", rotation="40kb")

    return gbv


if __name__ == '__main__':
    argv = terminal()
    if argv is None:
        exit(0)
    
    start = time.time()
    gbvObject = starter(
        url=argv['input'],
        browser=argv['browser'],
        outputDir=argv['output'],
        page=argv['page'],
        cookies=argv['cache'],
        IfStartCache=True if argv['cache'] else False,
        hwaccels=argv['hwaccels'],
        libx264=argv['libx264']
    )
    if "favlist" in argv['input']:
        gbvObject.GetAllFavlist()
    else:
        gbvObject.get()

    end = time.time()
    logger.info(f"总耗时：{end - start}")
    