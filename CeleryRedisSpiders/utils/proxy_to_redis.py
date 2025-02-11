import json
import redis
import requests
import schedule
import time
import datetime
from loguru import logger as log

redis_client = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=3,
    decode_responses=True
)


def extract_proxy_ips():
    proxy_api = ""
    dispose_ip_list = []

    try:
        resp_json = requests.get(proxy_api).json()
        log.info(f'resp_json: {resp_json}')
        now_day_hms = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if resp_json.get("code") == 'SUCCESS':
            proxy_data = resp_json.get('data', [])
            for i in proxy_data:
                proxyUrl = format_proxy(i['server'])
                deadline = i['deadline']

                if now_day_hms < deadline:
                    proxies = {
                        "http": proxyUrl,
                        "https": proxyUrl,
                    }
                    dispose_ip_list.append(proxies)
                else:
                    log.error(f'{proxyUrl} 过期')
        else:
            log.error('获取代理失败', resp_json)
    except Exception as e:
        log.error(f'发生错误: {e}')

    return dispose_ip_list


def format_proxy(proxy_ip_port):
    authKey = "4D81A157"
    password = "42E1293157A6"
    proxyUrl = f"http://{authKey}:{password}@{proxy_ip_port}"
    return proxyUrl


def update_proxy_ips():
    new_proxies = extract_proxy_ips()
    if new_proxies:
        redis_client.delete('ip_proxies')
        for proxy in new_proxies:
            redis_client.zadd('ip_proxies', {json.dumps(proxy): 0})
        log.success(f"更新代理: {new_proxies}")
    else:
        log.error("无法从 API 获取代理")


update_proxy_ips()

schedule.every(30).seconds.do(update_proxy_ips)

while True:
    schedule.run_pending()
    time.sleep(1)
