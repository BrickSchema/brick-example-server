import requests


class GrafanaEndpoint:
    def __init__(self, baseurl, apikey):
        self.baseurl = baseurl
        self.apikey = apikey

    async def get(self, path, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Authorization"] = "Bearer " + self.apikey
        kwargs["headers"] = headers
        url = self.baseurl + path
        resp = requests.get(url, **kwargs)
        # async with aiohttp.ClientSession() as session:
        #    async with session.post(url, **kwargs) as resp:
        #        return resp
        return resp

    async def post(self, path, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Authorization"] = "Bearer " + self.apikey
        kwargs["headers"] = headers
        url = self.baseurl + path
        resp = requests.post(url, **kwargs)
        # async with aiohttp.ClientSession() as session:
        #    async with session.post(url, **kwargs) as resp:
        #        return resp
        return resp
