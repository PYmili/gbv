from loguru import logger
from rookiepy import edge, chrome, firefox


class GetBrowserCookies:
    """
    获取浏览器的Bilili.co的Cookies值
    """
    def __init__(self, browser: int = 0) -> None:
        """
        :param browser: 通过int类型选择浏览器：0:edge、1:chrome、2:firefox
        :return None
        """
        self.domain_name = ".bilibili.com"
        self.cookies = None

        if browser == 0:
            self.cookies = edge()
        elif browser == 1:
            self.cookies = chrome()
        elif browser == 2:
            self.cookies = firefox()

    def get(self) -> str:
        """
        获取Cookies

        :return str
        """
        result = ""
        if self.cookies:
            for cookie in self.cookies:
                if cookie['domain'] == self.domain_name:
                    # print(cookie['name'], cookie['value'])
                    result += f"{cookie['name']}={cookie['value']}; "

        logger.info("成功获取Cookies")
        return result

    def getValue(self, key: str) -> str:
        """
        通过Cookies中的key获取value值。

        :param key: str
        :return str
        """
        for cookie in self.cookies:
            if cookie['domain'] == self.domain_name:
                if key == cookie['name']:
                    return cookie['value']

        return ""


if __name__ in "__main__":
    cookies = GetBrowserCookies()
    print(cookies.get())
    print(cookies.getValue("buvid4"))
