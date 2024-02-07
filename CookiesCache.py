"""
Cookies的缓存处理
"""
import os
import json

from loguru import logger


class CookiesCache:
    """Cookies的缓存"""
    def __init__(self) -> None:
        logger.info("启动Cookies缓存类")

    def Save(self, DomainName: str, Cookies: str) -> bool:
        OldJsonData = self.Read()
        with open(os.path.join(os.getcwd(), "cookies.json"), "w+", encoding="utf-8") as cookieWfp:
            OldJsonData[DomainName] = Cookies
            cookieWfp.write(json.dumps(OldJsonData))

    def Read(self) -> dict:
        logger.info("读取Cookies.json")
        result = {}
        if os.path.isfile(os.path.join(os.getcwd(), "cookies.json")) is False:
            return result
        with open(os.path.join(os.getcwd(), "cookies.json"), "r", encoding="utf-8") as cookieRfp:
            result = json.loads(cookieRfp.read())

        return result
    