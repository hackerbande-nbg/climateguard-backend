import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HttpClient:
    def __init__(self, retries=4, retry_on_status=None):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            status_forcelist=retry_on_status or [500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
            backoff_factor=0.3
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
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
