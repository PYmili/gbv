import requests
import browser_cookie3

cookieName = [
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


def GetCookie(browser: int) -> str:
    cookies = ""
    try:
        if browser == 0:
            bc = browser_cookie3.edge()
        elif browser == 1:
            bc = browser_cookie3.chrome()
        elif browser == 2:
            bc = browser_cookie3.firefox()
        for i in bc:
            if i.name in cookieName:
                cookies += i.name + "=" + i.value + "; "
    except:
        cookies =  str(open(f"{PATH}/.cookie", "r", encoding="utf-8").read())
    
    return cookies