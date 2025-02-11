import requests
import time
from utils.user_agent import *
from utils.get_one_ip import get_random_ip


def safe_request(url, retry=30):
    """带防护机制的请求函数"""
    for attempt in range(retry):
        try:
            headers = {'User-Agent': get()}
            resp = requests.get(url,
                                headers=headers,
                                # proxies=get_random_ip(),
                                timeout=(6, 10))
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            if attempt == retry - 1:
                raise
            time.sleep(2 ** attempt)
    return None
