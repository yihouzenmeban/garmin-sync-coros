GARTH_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def configure_domain(garth_module, auth_domain: str) -> str:
    if auth_domain and str(auth_domain).upper() == "CN":
        domain = "garmin.cn"
    else:
        domain = "garmin.com"
    garth_module.configure(domain=domain)
    return domain


def apply_browser_user_agent(garth_module) -> None:
    garth_module.client.sess.headers["User-Agent"] = GARTH_BROWSER_USER_AGENT


def remove_garth_user_agent(garth_module) -> None:
    garth_module.client.sess.headers.pop("User-Agent", None)
