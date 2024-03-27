import os
from typing import Dict, Union

import requests
from urllib.parse import urlsplit
from fileid.fileid import Newid
from tqdm import tqdm
from loguru import logger

import GenerateHeaders
import bvid_aid
import FavoriteCrawling
import CookiesCache
import methods

ARC_API_URL = "https://api.bilibili.com/x/space/top/arc?vmid="


class DownloadBilibiliFile:
    """下载Bilibili中的文件"""
    def __init__(
            self,
            url: str,
            headers: Dict[str, str],
            SavePath: str
    ) -> None:
        """
        下载 Bilibili 中的文件
        :param url: 链接
        :param headers: 请求头
        :param SavePath: 保存路径
        """
        logger.info(f"下载文件：{url}")
        response = requests.get(url, headers=headers, stream=True)
        FpTqdm = tqdm(total=len(response.content) // 8192 + 1)

        try:
            with open(SavePath, "wb") as fp:
                for chunk in response.iter_content(chunk_size=8192):
                    fp.write(chunk)
                    FpTqdm.update(1)
        except OSError as OSE:
            logger.error(f"发生错误: {OSE}")

        # all close
        FpTqdm.close()
        response.close()
        logger.info("下载成功！")


class GBV:
    """主类"""
    def __init__(
            self,
            url: str,
            browser: int,
            params: dict,
            outputDir: str = os.getcwd(),
            args: Union[dict, None] = None,
            cookies: Union[str, bool] = False,
            IfStartCache: bool = True,
            hwaccels: Union[str, False] = False,
            libx264: bool = False
    ) -> None:
        """
        主类

        :param cookies: 自定义cookies值
        :param page: 要下载的页数
        :param outputDir: 输出路径
        :param url: 要访问的 URL 地址
        :param browser: 选择要获取 cookies 的浏览器
        :param IfStartCache: 是否开启Cookie缓存
        :param hwaccels: 给ffmpeg添加硬件加速
        :param libx264: 是否转换为h.264编码
        :return None
        """
        logger.info("启动主类")
        self.url = url
        self.params = params
        self.outputDir = outputDir
        self.args = args
        self.cookies = cookies
        self.IsStartCache = IfStartCache
        self.CookieCache = CookiesCache.CookiesCache()
        self.hwaccels = hwaccels
        self.libx264 = libx264
        self.browser = browser
        self.headers = GenerateHeaders.generate(browser, self.cookies)

        # 判断是否打开cookies缓存
        if IfStartCache is True:
            for CacheKey, CacheValue in self.CookieCache.Read().items():
                if CacheKey == urlsplit(self.url).netloc.split(".", 1)[-1]:
                    logger.info(f"检查到Cookies缓存，立即使用：{CacheKey}")
                    self.headers = GenerateHeaders.generate(browser, CacheValue)

        # title：视频名称，audio_url：视频链接，video_url：视频链接
        self.title = None
        self.audio_url = None
        self.video_url = None
        self.video_type = ".mp4"
        self.fav_links = []

    def _fileOutputAndMove(self, file: str, toPath: str) -> str:
        """
        文件的输出和移动
        :param file: 要处理的文件
        :param toPath: 移至此文件夹
        :return: str
        """
        # 文件存在直接读取，不存在则返回空字符串
        if os.path.isfile(file):
            rfp = open(file, "rb")
        else:
            return ""

        # 判断移动至目录是否存在
        if os.path.isfile(toPath) is False:
            if os.path.isdir(toPath):
                toPath = os.path.join(toPath, self.title + self.video_type)
            else:
                return ""
        
        # 正式开始移动
        try:
            with open(toPath, "wb") as wfp:
                wfp.write(rfp.read())
        except OSError:
            toPath = os.path.join(self.outputDir, Newid(10).newfileid() + self.video_type)
            with open(toPath, "wb") as wfp:
                wfp.write(rfp.read())

        rfp.close()
        os.remove(file)
        logger.info(f"成功移动 {file} -> {toPath}")
        return toPath

    def save(self) -> bool:
        """
        保存及处理文件
        :return: bool
        """
        randomStr = os.path.join(os.getcwd(), Newid(5).newfileid() + self.video_type)
        tempMp4Path = os.path.join(os.getcwd(), "temp.mp4")
        tempMp3Path = os.path.join(os.getcwd(), "temp.mp3")
        FFmepgPath = os.path.join(os.getcwd(), "ffmpeg.exe")

        if os.path.isfile(FFmepgPath) is False:
            if methods.find_ffmpeg():
                FFmepgPath = methods.find_ffmpeg()
            else:
                logger.error("未找到ffmpeg！")
                return False
            
        # 如果文件存在，则停止下载。
        is_file = os.path.join(self.outputDir, os.path.split(self.outputDir)[-1] + self.video_type)
        if os.path.isfile(is_file) is True:
            logger.warning("识别到文件已存在，停止下载。")
            return True

        logger.info("开始下载音频")
        DownloadBilibiliFile(self.audio_url, self.headers, tempMp3Path)

        logger.info("开始下载视频")
        DownloadBilibiliFile(self.video_url, self.headers, tempMp4Path)

        # 将视频拼接
        parameter = fr"-c:v copy -c:a copy -bsf:a aac_adtstoasc " + randomStr
        if self.libx264 is True:
            # 转换为H.264编码，适配windows平台
            parameter = "-c:v libx264 -preset slow -crf 28 -c:a copy " + randomStr
        if self.hwaccels:
            cmd = fr"{FFmepgPath} -y -hwaccel {self.hwaccels} " \
                  fr"-i {tempMp4Path} -i {tempMp3Path} " + parameter
        else:
            cmd = fr"{FFmepgPath} -y -i {tempMp4Path} -i {tempMp3Path} " + parameter
        logger.info(fr"执行命令：\"{cmd}\"")
        os.popen(cmd).read()

        moveReturn = self._fileOutputAndMove(f"{randomStr}", self.outputDir)

        logger.info("删除缓存文件")
        os.remove(tempMp4Path)
        os.remove(tempMp3Path)

        logger.info(f"成功！视频保存文件为：{moveReturn}")

        # 是否保存cookies
        if self.cookies:
            self.CookieCache.Save(
                DomainName=urlsplit(self.url).netloc.split(".", 1)[-1],
                Cookies=self.cookies
            )
        return True

    def GetAllFavlist(self) -> None:
        """
        收藏夹爬取
        :param bvid: str
        :return: None
        """

        # 判断是否为收藏夹链接
        SplitUrl = self.url.split("/")
        if "favlist" != SplitUrl[-1].split("?")[0]:
            logger.warning("检测到链接并不是收藏夹")
            return None

        # 检测传入的参数
        if not self.args:
            logger.warning(f"检测到参数缺失，args: {self.args}")
            return None

        # 通过page获取url
        if self.args['page'] != 0:
            for page in self.args['page']:
                links = FavoriteCrawling.FavoriteCrawling(
                    url=self.url,
                    headers=self.headers,
                    page=page
                ).run()

                for link in links:
                    self.fav_links.append(link)
        else:
            self.fav_links = FavoriteCrawling.FavoriteCrawling(
                url=self.url,
                headers=self.headers
            ).run()

        __cacheDir = self.outputDir
        for fav_link in self.fav_links:
            self.url = fav_link
            # 获取title, audio, video
            data = methods.GetPlayInfoData(
                url=fav_link,
                headers=self.headers,
                params=self.params
            )
            if data is None:
                continue

            self.title = data['title']
            self.video_url = data['video']
            self.audio_url = data['audio']
            self.outputDir = methods.CurrentFolderEvent(
                self.title,
                __cacheDir
            )

            # 尝试保存，未保存成功将执行
            if self.save() is False:
                os.removedirs(self.outputDir)
                logger.error("保存失败！将退出程序！")
                exit(0)

        logger.info("收藏夹视频下载完成！")

    def get(self) -> None:
        """
        获取链接中的视频
        :return: None
        """
        cookiesCache = False
        if self.IsStartCache is True:
            for CacheKey, CacheValue in self.CookieCache.Read().items():
                if CacheKey == urlsplit(self.url).netloc.split(".", 1)[-1]:
                    cookiesCache = CacheValue

        # 获取视频的page页数（未来可能抛弃）
        VideoPage = methods.GetUrlPage(
            params={
                "bvid": self.params['bvid'],
                "aid": bvid_aid.getAID(self.params['bvid'], cookiesCache, self.browser),
            },
            headers=self.headers
        )
        logger.info(f"下载 page: {VideoPage}")

        self.params = {
            "p": VideoPage
        }
        data = methods.GetPlayInfoData(
            url=self.url,
            headers=self.headers,
            params=self.params
        )
        if not data:
            logger.error("未获取到标题，音频，视频链接！")
            return None

        self.title = data['title']
        self.video_url = data['video']
        self.audio_url = data['audio']
        self.outputDir = methods.CurrentFolderEvent(
            self.title,
            self.outputDir
        )
        self.save()
