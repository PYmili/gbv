import requests
import GenerateHeaders


def getAID(bvid: str, cookieCache: dict) -> int:
    aid = None
    url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
    if cookieCache:
        headers = GenerateHeaders.generate(cookies=cookieCache)
    else:
        headers = GenerateHeaders.generate()

    with requests.get(url, headers=headers) as get:
        if get.status_code == 200:
            aid = get.json()['data']['aid']
    
    return aid