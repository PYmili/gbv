import browser_cookie3


class GetBrowser_cookies:
    def __init__(self, browser: int = 0) -> None:
        self.CookieKeys = [
            "buvid4",
            "b_nut",
            "b_lsid",
            "buvid3",
            "i-wanna-go-back",
            "_uuid",
            "FEED_LIVE_VERSION",
            "home_feed_column",
            "browser_resolution",
            "buvid_fp",
            "header_theme_version",
            "PVID",
            "SESSDATA",
            "bili_jct",
            "DedeUserID",
            "DedeUserID__ckMd5",
            "b_ut",
            "CURRENT_FNVAL",
            "sid",
            "rpdid"
        ]

        try:
            if browser == 0:
                self.browserCookies = browser_cookie3.edge()
            if browser == 1:
                self.browserCookies = browser_cookie3.chrome()
            if browser == 2:
                self.browserCookies = browser_cookie3.firefox()
        except browser_cookie3.BrowserCookieError:
            self.browserCookies = None

        except PermissionError as PE:
            self.browserCookies = None
            raise PermissionError(f"{PE}\n可能是浏览器引起的问题，可以尝试重装浏览器")

    def get(self) -> str:
        cookies = ""
        for i in self.browserCookies:
            if i.name in self.CookieKeys:
                cookies += f"{i.name}={i.value}; "

        return cookies

    def getValue(self, key: str) -> str:
        for i in self.browserCookies:
            if key == i.name:
                return i.value
        return ""
