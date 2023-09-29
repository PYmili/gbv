import requests
import getHeaders


def getAID(bvid: str, cookieCache: dict) -> int:
    aid = None
    url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
    if cookieCache:
        headers = getHeaders.get(cookies=cookieCache)
    else:
        headers = getHeaders.get()

    with requests.get(url, headers=headers) as get:
        if get.status_code == 200:
            aid = get.json()['data']['aid']
    
    return aid