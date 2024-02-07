import GetBilibiliCookies

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
REFERER = "https://www.bilibili.com/"


def generate(browser: int = 0, cookies: str = False) -> dict:
    return {
        "User-Agent": USER_AGENT,
        "cookie": GetBilibiliCookies.GetBrowserCookies(browser).get() if cookies is False else cookies,
        "Referer": REFERER
    }