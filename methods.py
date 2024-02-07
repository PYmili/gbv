import os
import json
import subprocess
from glob import glob
from typing import Union

import requests
from fileid.fileid import Newid
from bs4 import BeautifulSoup
from loguru import logger

DETAIL_API_URL = "https://api.bilibili.com/x/web-interface/wbi/view/detail"


def find_ffmpeg() -> Union[str, None]:
    """
    在系统PATH环境变量包含的目录下搜索ffmpeg.exe
    """
    for path in os.environ["PATH"].split(os.pathsep):
        ffmpeg_exe = os.path.join(path, "ffmpeg.exe")
        if os.path.isfile(ffmpeg_exe):
            return ffmpeg_exe
    return None


def sanitize_filename(filename):
    # 使用translate方法配合maketrans创建映射表，将非法字符替换为空字符串
    sanitized = filename.translate(str.maketrans('', '', r'\/:*?"<>|.'))
    
    # 返回处理过的安全文件名
    return sanitized


def CurrentFolderEvent(dirName: str, outputDir: str = os.getcwd()) -> str:
    """
    当前文件夹事件
    :param dirName: 目录名称
    :param outputDir: 输出目录
    :return:
    """
    result = outputDir

    if outputDir == os.getcwd():
        logger.info(f"在当前位置，创建输出文件夹")
        try:
            result = os.path.join(
                os.getcwd(),
                dirName
            )
            if os.path.isdir(result) is False:
                os.makedirs(result)
        except OSError as e:
            logger.warning(f"发生{e}错误，程序将随机生成文件夹名。")
            result = os.path.join(
                os.getcwd(),
                Newid(10).newfileid()
            )
            if os.path.isdir(result) is False:
                os.makedirs(result)

    return result


def GetUrlPage(params: dict, headers: dict) -> int:
    """
    获取视频的page
    
    :param params:
    :param headers:
    :return:
    """
    logger.info("获取视频page")
    result = 1

    with requests.get(DETAIL_API_URL, params=params, headers=headers) as response:
        if response.status_code == 200:
            result = len(response.json()['data']['View']['pages'])
        else:
            logger.warning("获取页数失败！将默认下载单页")
            result = 1

    return result


def GetPlayInfoData(url: str, headers: dict, params: dict) -> Union[dict, None]:
    """
    获取视频，音频链接(window.__playinfo__)
    :param url:
    :param headers:
    :param params:
    :return: Union[dict, None]
    """
    logger.info("获取视频，音频链接(window.__playinfo__)")

    result = None

    with requests.get(url, headers=headers, params=params) as response:
        if response.status_code == 200:
            try:
                title = BeautifulSoup(response.text, "lxml").find("h1", class_="video-title").attrs['title']
                logger.info(f"获取到Title -> {title}")
            except AttributeError:
                logger.warning(f"{url}，请求时出现错误，视频已被删除！")
                return result
            title = sanitize_filename(title)
            
            PlayInfo = BeautifulSoup(response.text, "lxml").find_all("script")[3].text.split("=", 1)[-1]

            if not PlayInfo:
                return result
            try:
                PlayInfo = json.loads(PlayInfo)
                logger.info("成功获取到视频，音频数据")
            except Exception as e:
                logger.error(f"获取视频，音频数据时发生错误 -> {e}")
                exit(0)
            
            result
            result = {
                "title": title,
                "video": PlayInfo['data']['dash']['video'][0]['baseUrl'],
                "audio": PlayInfo['data']['dash']['audio'][0]['baseUrl']
            }
        else:
            logger.warning(f"{url}，请求时出现错误，可能是视频已消失。")

    return result


def get_ffmpeg_hwaccels():
    # 调用ffmpeg命令获取硬件加速方法
    result = subprocess.run(['ffmpeg', '-hwaccels'], capture_output=True, text=True)
    # 解析输出以提取硬件加速方法列表
    lines = result.stdout.split('\n')

    hwaccels = []
    for i in lines[1:]:
        i = i.strip()
        if i:
            hwaccels.append(i)

    return hwaccels
