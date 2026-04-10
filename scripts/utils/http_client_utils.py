import os

import certifi
import urllib3


def build_http_client():
    proxy_url = (
        os.environ.get("HTTPS_PROXY")
        or os.environ.get("https_proxy")
        or os.environ.get("HTTP_PROXY")
        or os.environ.get("http_proxy")
    )
    manager_kwargs = {
        "cert_reqs": "CERT_REQUIRED",
        "ca_certs": certifi.where(),
    }
    if proxy_url:
        return urllib3.ProxyManager(proxy_url, **manager_kwargs)
    return urllib3.PoolManager(**manager_kwargs)
