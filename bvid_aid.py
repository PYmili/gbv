import requests

import getHeaders

def getAID(bvid: str) -> int:
    aid = None
    url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
    with requests.get(url, headers=getHeaders.get()) as get:
        if get.status_code == 200:
            aid = get.json()['data']['aid']
    
    return aid