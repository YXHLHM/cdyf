import json
import random
import redis

redis_client = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=3,
    decode_responses=True
)


def get_random_ip():
    try:
        # 从 Redis 的有序集合中获取所有元素
        proxies = redis_client.zrange('ip_proxies', 0, -1)

        if proxies:
            # 随机选择一个元素
            random_proxy_json = random.choice(proxies)
            random_proxy = json.loads(random_proxy_json)

            return random_proxy
        else:
            print("没有获取到代理 IP")
            return None
    except Exception as e:
        print(f"获取随机 IP 时出错: {e}")
        return None


# random_ip = get_random_ip()
# if random_ip:
#     print(f"随机获取到的 IP 代理是: {random_ip}")



