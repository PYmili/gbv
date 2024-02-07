import requests
from loguru import logger


class FavoriteCrawling:
    def __init__(self, url: str, headers: dict, page: int = 0) -> None:
        self.headers = headers
        self.fid = url.split("fid=")[-1].split("&", 1)[0]
        self.page = page
        self.url = url
        self.api_url = "https://api.bilibili.com/x/v3/fav/resource/list"

    def run(self) -> list:
        params = {
            'media_id': self.fid,
            'ps': 20
        }

        links = []

        if self.page == 0:
            count = 1
            while True:
                params['pn'] = count
                with requests.get(self.api_url, headers=self.headers, params=params) as get:
                    if get.status_code == 200:
                        getResult = get.json()
                        if getResult['code'] == 400:
                            break
                        medias = getResult['data']['medias']
                        try:
                            for i in medias:
                                links.append("https://www.bilibili.com/video/"+i['bv_id']+'/')
                        except TypeError:
                            break
                    else:
                        logger.warning(f"向接口{self.api_url}请求无效！")

                count += 1
        else:
            params['pn'] = self.page
            with requests.get(self.api_url, headers=self.headers, params=params) as get:
                if get.status_code == 200:
                    getResult = get.json()
                    if getResult['code'] == 400:
                        logger.error("未找到此页！")
                        return []
                    medias = getResult['data']['medias']
                    for i in medias:
                        links.append("https://www.bilibili.com/video/" + i['bv_id'] + '/')
                else:
                    logger.warning(f"向接口{self.api_url}请求无效！")

        logger.info(f"抓取收藏夹链接完毕，共{len(links)}个。")
        return links
    