import GetBilibiliCookies

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
REFERER = "https://www.bilibili.com/"


def get(browser: int = 0) -> dict:
    return {
        "User-Agent": USER_AGENT,
        "cookie": GetBilibiliCookies.GetBrowser_cookies(browser).get(),
        "Referer": REFERER
    }