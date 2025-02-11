import json
import os

from celery import Celery
from config import CeleryConfig, DETAIL_BUFFER_REDIS_URL
from utils.http_client import safe_request
from utils.parser import parse_list_page, parse_detail_page
import pandas as pd
from loguru import logger as log
import redis
from utils.public_func import get_md5

# 存储位置
file_path = 'pubmed_article_data.csv'
# 创建 Celery 应用实例并加载配置
app = Celery('crawler_tasks')
app.config_from_object(CeleryConfig)

# Redis 实例
redis_client = redis.Redis.from_url(DETAIL_BUFFER_REDIS_URL)
DETAIL_BUFFER_KEY = "detail_data_buffer"  # 用于暂存详情数据的 Redis key
DETAIL_URL_SET_KEY = "detail_url_set"  # 用于存储已请求的详情页 URL 防止重复


@app.task(name='process_list_page',
          autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3, 'countdown': 5},
          queue="list_queue")
def process_list_page(list_url):
    """
    处理列表页任务
      - 请求列表页
      - 解析详情页 URL 列表
      - 提交详情页任务
    """
    try:
        # 发送请求（包含自动重试）
        list_resp_text = safe_request(list_url)

        # 解析列表页，得到详情页
        detail_items = parse_list_page(list_resp_text)

        # 提交详情页url任务到队列
        for detail_url in detail_items:
            process_detail_page.delay(detail_url)

        return {"status": "success", "items_count": len(detail_items)}
    except Exception as e:
        log.error(f"List task failed: {list_url}, error: {str(e)}")
        raise


@app.task(name='process_detail_page',
          autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 5, 'countdown': 10},
          queue="detail_queue", rate_limit='10/s')
def process_detail_page(detail_url):
    """
    处理详情页任务：
      - 请求详情页
      - 解析详情页数据
      - 将解析后的数据以 JSON 形式存入 Redis 缓冲区，待批量入库
    """
    try:
        # 防止重复请求
        url_hash = get_md5(detail_url.encode('utf-8'))
        if redis_client.sismember(DETAIL_URL_SET_KEY, url_hash):
            return {"status": "skipped", "url": detail_url, "message": f"该详情页已处理过，跳过: {detail_url}"}

        detail_resp_text = safe_request(detail_url)
        data = parse_detail_page(detail_resp_text, detail_url)

        # 将解析后的数据存入 Redis 缓冲区（存储为 JSON 字符串）
        redis_client.rpush(DETAIL_BUFFER_KEY, json.dumps(data))

        # 标记此 URL 已经被处理
        redis_client.sadd(DETAIL_URL_SET_KEY, url_hash)

        return {"status": "success", "url": detail_url}
    except Exception as e:
        log.error(f"详情页任务失败: {detail_url}, 错误: {str(e)}")
        raise


@app.task(name='bulk_save_detail_data', queue='periodic_queue')
def bulk_save_detail_data(batch_size=1000):
    """
        定时任务：从 Redis 缓冲区中批量取出详情数据，并批量写入数据库
        去重：
            -通过详情页url可以达到去重的效果，商品的状态是可以根据网页的筛选进行判断（勾选只看有效所展示的详情页url就是有效，反之过期），
            -但是其详情内容的其他可能会变的（暂时不考虑）
    """
    batch_items = []
    for _ in range(batch_size):
        item_json = redis_client.lpop(DETAIL_BUFFER_KEY)
        if not item_json:
            break
        data = json.loads(item_json)
        batch_items.append(data)
    if batch_items:
        try:
            df = pd.DataFrame(batch_items)
            if os.path.exists(file_path):
                df.to_csv(file_path, index=False, mode='a', header=False)  # todo
            else:
                df.to_csv(file_path, index=False, mode='w', header=True)  # todo
            # log.success(f"批量写入有 {len(batch_items)} 条")
            return {"status": "success", "message": f"批量存储 {len(batch_items)} 条详情数据成功"}

        except Exception as e:
            log.error(f"批量存储数据失败: {e}")
            # 如果存储失败，就将数据重新推回 Redis 以便后续重试 生产应该考虑到哪一条
            for r_data in batch_items:
                redis_client.lpush(DETAIL_BUFFER_KEY, json.dumps(r_data))
            return {"status": "failed", "message": "数据存储失败，将数据重新推回 Redis 以便后续重试"}
    else:
        return {"status": "normal", "message": "无详情数据待存储，等待数据"}
