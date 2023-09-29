import json
import sys
import os
import getopt

import requests
from urllib.parse import urlsplit
from fileid.fileid import Newid
from tqdm import tqdm
from loguru import logger
from bs4 import BeautifulSoup

import getHeaders
import bvid_aid
import FavoriteCrawling


PATH: str = os.path.split(__file__)[0]
COOKIE: bool = False
OUTPUTPATH: str = PATH
PAGE: list = [
    None
]


class CookiesCache:
    def __init__(self) -> None:
        logger.info("启动Cookies缓存类")

    def Save(self, DomainName: str, Cookies: str) -> bool:
        OldJsonData = self.Read()
        with open(".\\cookies.json", "w+", encoding="utf-8") as cookieWfp:
            OldJsonData[DomainName] = Cookies
            cookieWfp.write(json.dumps(OldJsonData))

    def Read(self) -> dict:
        logger.info("读取Cookies.json")
        result = {}
        if os.path.isfile(".\\cookies.json") is False:
            return result
        with open(".\\cookies.json", "r", encoding="utf-8") as cookieRfp:
            result = json.loads(cookieRfp.read())

        return result


def CurrentFolderEvent(dirName: str) -> None:
    global OUTPUTPATH

    if OUTPUTPATH == os.path.split(__file__)[0]:
        logger.info(f"在当前位置，创建输出文件夹")
        try:
            OUTPUTPATH = os.path.join(
                os.getcwd(),
                dirName
            )
            if os.path.isdir(OUTPUTPATH) is False:
                os.mkdir(OUTPUTPATH)
        except OSError as e:
            logger.warning(f"发生{e}错误，程序将随机生成文件夹名。")
            OUTPUTPATH = os.path.join(
                os.getcwd(),
                Newid(10).newfileid()
            )
            if os.path.isdir(OUTPUTPATH) is False:
                os.mkdir(OUTPUTPATH)


class GBV:
    def __init__(
            self,
            _url: str,
            _browser: int,
            _params: dict,
            _isStartCache: bool = True
    ) -> None:
        """
        主类
        :param _url: str，要访问的 URL 链接
        :param _browser: int，选择要获取 cookies 的浏览器
        :param _params: dict 参数
        :param _isStartCache: bool 是否启动缓存检查
        """
        logger.info("启动主类")
        self.url = _url
        self.params = _params
        self.CookieCache = CookiesCache()
        self.headers = None
        if _isStartCache is True:
            for CacheKey, CacheValue in self.CookieCache.Read().items():
                if CacheKey == urlsplit(self.url).netloc.split(".", 1)[-1]:
                    logger.info(f"检查到Cookies缓存，立即使用：{CacheKey}")
                    self.headers = getHeaders.get(_browser, CacheValue)
        if self.headers is None:
            self.headers = getHeaders.get(_browser, COOKIE)

        self.title = None
        self.audio = None
        self.video = None

        self.fav_links = []

    def move(self, file: str, toPath: str) -> str:
        """
        文件的输出，移动
        :param file: str，要处理的文件
        :param toPath: str，移至此文件夹
        :return: str
        """
        if os.path.isfile(file):
            rfp = open(file, "rb")
        else:
            return None

        if os.path.isfile(toPath) is False:
            if os.path.isdir(toPath):
                toPath = os.path.join(toPath, self.title+".mp4")
            else:
                return None
        try:
            with open(toPath, "wb") as wfp:
                wfp.write(rfp.read())
        except OSError:
            toPath = os.path.join(OUTPUTPATH, Newid(10).newfileid()+".mp4")
            with open(toPath, "wb") as wfp:
                wfp.write(rfp.read())

        rfp.close()
        os.remove(file)
        logger.info(f"成功移动 {file} -> {toPath}")
        return toPath

    def GetPlayInfoData(self) -> tuple:
        """
        获取<script>window.__playinfo__=...</script> 参数
        :return: tuple
        """
        logger.info("获取视频，音频链接(window.__playinfo__)")
        with requests.get(self.url, headers=self.headers, params=self.params) as get:
            if get.status_code == 200:
                try:
                    self.title = BeautifulSoup(get.text, "lxml").find("h1", class_="video-title").attrs['title']
                    logger.info(f"获取到Title -> {self.title}")
                except AttributeError:
                    logger.warning(f"{self.url}，请求时出现错误，视频已被删除！")
                    return False
            
                for script in BeautifulSoup(get.text, "lxml").find_all("script"):
                    script = script.text.split("=", 1)
                    if "window.__playinfo__" == script[0]:
                        data = script[-1]
                try:
                    data = json.loads(data)
                    logger.info("成功获取到视频，音频数据")
                except Exception as e:
                    logger.error(f"获取视频，音频数据时发生错误 -> {e}")
                    exit(0)
            
                self.audio = data['data']['dash']['audio'][0]['baseUrl']
                self.video = data['data']['dash']['video'][0]['baseUrl']
            else:
                logger.warning(f"{self.url}，请求时出现错误，可能是视频已消失。")

        return self.title, self.audio, self.video

    def save(self) -> None:
        """
        保存及处理文件
        :return: None
        """
        randomStr = os.path.join(os.getcwd(), Newid(5).newfileid()+".mp4")
        output_path = os.path.join(os.getcwd(), "output.mp4")
        tempMp4_Path = os.path.join(os.getcwd(), "temp.mp4")
        tempMp3_Path = os.path.join(os.getcwd(), "temp.mp3")
        ffmepg_Path = os.path.join(PATH, "ffmpeg.exe")

        logger.info("开始下载音频")
        with requests.get(self.audio, headers=self.headers, stream=True) as AudioGet:
            FpAudioTqdm = tqdm(total=len(AudioGet.content) // 8192 + 1)

            with open(tempMp3_Path, "wb") as fp_audio:
                for chunk in AudioGet.iter_content(chunk_size=8192):
                    fp_audio.write(chunk)
                    FpAudioTqdm.update(1)
                fp_audio.close()
            FpAudioTqdm.close()

        logger.info("开始下载视频")
        with requests.get(self.video, headers=self.headers, stream=True) as VideoGet:
            FpVideoTqdm = tqdm(total=len(VideoGet.content) // 8192 + 1)

            with open(tempMp4_Path, "wb") as fp_video:
                for chunk in VideoGet.iter_content(chunk_size=8192):
                    fp_video.write(chunk)
                    FpVideoTqdm.update(1)
                fp_video.close()
            FpVideoTqdm.close()

        cmd = fr"{ffmepg_Path} -y -i {tempMp4_Path} {output_path}"
        logger.info(fr"执行命令：\"{cmd}\"")
        os.popen(cmd).read()

        cmd = fr"{ffmepg_Path} -y -i {output_path} -i {tempMp3_Path} -c:v copy -c:a copy -bsf:a aac_adtstoasc {randomStr}"
        logger.info(fr"执行命令：\"{cmd}\"")
        os.popen(cmd).read()

        moveReturn = self.move(f"{randomStr}", OUTPUTPATH)
        
        logger.info("删除缓存文件")
        os.remove(tempMp4_Path)
        os.remove(tempMp3_Path)
        os.remove(output_path)
        
        logger.info(f"成功！视频保存文件为：{moveReturn}")

        if COOKIE:
            self.CookieCache.Save(
                DomainName=urlsplit(self.url).netloc.split(".", 1)[-1],
                Cookies=COOKIE
            )

    def run(self, bvid: str) -> None:
        """
        :param bvid: str
        :return:
        """
        global OUTPUTPATH

        if "favlist" == self.url.split("/")[-1].split("?")[0]:
            if PAGE[0] != "ALL" and PAGE[0] is not None:
                for i in PAGE:
                    links = FavoriteCrawling.FavoriteCrawling(
                        url=self.url,
                        headers=self.headers,
                        page=i
                    ).run()
                    for link in links:
                        self.fav_links.append(link)
            else:
                self.fav_links = FavoriteCrawling.FavoriteCrawling(
                    url=self.url,
                    headers=self.headers
                ).run()

            RECORDPOINT = OUTPUTPATH
            for link in self.fav_links:
                self.url = link
                result = self.GetPlayInfoData()
                if result is False:
                    OUTPUTPATH = RECORDPOINT
                    continue
                CurrentFolderEvent(result[0])
                self.save()
                OUTPUTPATH = RECORDPOINT

            logger.info("收藏夹视频下载完成！")
            return None

        api_url = "https://api.bilibili.com/x/web-interface/wbi/view/detail"
        params = {
            "bvid": bvid,
            "aid": bvid_aid.getAID(bvid),
        }
        videos = {}

        logger.info("获取视频page")
        with requests.get(api_url, params=params, headers=self.headers) as get:
            page_all = 1
            for i in get.json()['data']['View']['pages']:
                videos[i['page']] = i['part']
                page_all += 1

            CurrentFolderEvent(get.json()['data']['View']['title'])

            if PAGE[0] == "ALL":
                logger.info("下载视频所有page")
                for key, value in videos.items():
                    self.params = {
                        "p": i
                    }
                    self.GetPlayInfoData()
                    self.title = value
                    self.save()
            elif (type(PAGE) == list) and (PAGE[0] is not None):
                logger.info(f"下载指定page: {PAGE}")
                for i in PAGE:
                    if i <= int(page_all):
                        self.params = {
                            "p": i
                        }
                        self.GetPlayInfoData()
                        self.title = f"{i}."+videos[i]
                        self.save()
            elif PAGE[0] is None:
                self.GetPlayInfoData()
                self.save()


def main(_url: str, _browser: int, bvid: str, params: dict, IsStartCache: bool) -> None:
    """
    :param _url: str，要访问的 URL 地址
    :param _browser: int，选择要获取 cookies 的浏览器
    :param bvid: str，用于向bilibili.com发送请求时的参数
    :param params: dict，参数
    :return: None
    """
    gbv = GBV(_url, _browser, params, IsStartCache)
    gbv.run(bvid)


def menu() -> None:
    print("""
    ########################################################################
    #   Get Bilibili Video (gbv)
    #   Author: PYmili
    #   Email: mc2005wj@163.com
    ########################################################################

        Command:
            --cookie or -c [Url Cookies]
            --input_url or -i [Video URL]
            --browser or -b [edge(default), chrome, firefox]
            --output or -o [Output file or path]
            --page or -p [start-end / all] Select an array of videos to download
    """)


if __name__ == '__main__':
    URL = None
    BROWSER = 0
    BVID = None
    IsStartCache = True
    PARAMS = {}

    logger.add(".\\log\\latest.log", rotation="40kb")

    options, argv = getopt.getopt(
        sys.argv[1:], "i:c:b:o:p:",
        [
            "input_url=",
            "cookie=",
            "closeCache",
            "cc",
            "browser=",
            "output=",
            "page="
        ]
    )

    for key, value in options:
        if key in ["-i", "--input_url"]:
            splitValue = value.split("video")[-1]
            splitValue = splitValue.split("/", 1)[-1].split("/", 1)
            URL = value
            BVID = splitValue[0]
            if splitValue[-1]:
                for i in splitValue[-1][1:].split("&"):
                    try:
                        PARAMS[i.split("=")[0]] = eval(i.split('=')[-1])
                    except SyntaxError:
                        PARAMS[i.split("=")[0]] = str(i.split('=')[-1])
            logger.info(f"更新参数：Url:{URL}, BVID:{BVID}, PARANS:{PARAMS}")
        if key in ["-c", "--cookie"]:
            COOKIE = value
            logger.info(f"更新cookie：{COOKIE}")
        if key in ["--cc", "--closeCache"]:
            IsStartCache = False
            logger.info("将不会检查Cookies缓存。")
        if key in ["-b", "--browser"]:
            if value == "chrome":
                BROWSER = 1
                logger.info("更新浏览器选择：chrome")
            elif value == "firefox":
                BROWSER = 2
                logger.info("更新浏览器选择：firefox")
        if key in ["-o", "--output"]:
            if os.path.isdir(value):
                OUTPUTPATH = value
                logger.info(f"更新输出路径：{OUTPUTPATH}")
            else:
                logger.warning(f"没有：{value} 这个路径。")
        if key in ["-p", "--page"]:
            if "-" in value:
                start, end = value.split("-")
                PAGE = [i for i in range(int(start), int(end)+1)]
            elif value in ["all", "ALL", "All"]:
                PAGE[0] = "ALL"
            else:
                PAGE[0] = int(value)
                # PAGE.append(int(value))
            logger.info(f"更新下载页数：{PAGE}")

    if URL is not None and BVID is not None:
        main(URL, BROWSER, BVID, PARAMS, IsStartCache)
        logger.info("程序正常退出...")
    else:
        menu()