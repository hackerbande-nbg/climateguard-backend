import requests
from requests.adapters import HTTPAdapter


class HttpClient:
    def __init__(self, retries=4, retry_on_status=None):
        self.session = requests.Session()
        adapter = HTTPAdapter()
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    def post(self, url, **kwargs):
        return self.session.post(url, **kwargs)

    def put(self, url, **kwargs):
        return self.session.put(url, **kwargs)

    def delete(self, url, **kwargs):
        return self.session.delete(url, **kwargs)
