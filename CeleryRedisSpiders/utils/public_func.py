import copy
import hashlib
import json
import random
import re
import time
from datetime import datetime
from loguru import logger as log


#####################################################################################################################
def timestamp_to_date(timestamp, time_format="%Y-%m-%d %H:%M:%S"):
    """
    @summary:
    ---------
    @param timestamp: 将时间戳转化为日期
    @param format: 日期格式
    ---------
    @result: 返回日期
    """
    if timestamp is None:
        raise ValueError("timestamp is null")

    date = time.localtime(timestamp)
    return time.strftime(time_format, date)


def get_md5(*args):
    """
    @summary: 获取唯一的32位md5
    ---------
    @param *args: 参与联合去重的值
    ---------
    @result: f5e03755a7cad5c153c5aea400b90ae4
    """

    m = hashlib.md5()
    for arg in args:
        m.update(str(arg).encode())

    return m.hexdigest()


def extract_price(price_text):
    # 使用正则表达式提取价格部分（支持整数和小数）
    match = re.search(r'\d+(?:\.\d+)?', price_text)
    if match:
        return float(match.group())
    return None


def del_title(title_str):
    if title_str:
        # 去除所有 HTML 标签
        clean_title = re.sub(r'<[^>]+>', '', title_str).strip()
        return clean_title
    return ''


def deal_str(content_str):
    """
    summary: 处理换\r\n\t
    """
    if content_str:
        return content_str.strip().replace('\r', '').replace('\n', '').replace('\t', '') if content_str else ''
    else:
        return ''



def deal_pub_time(date_str):
    """
    :return:  格式化输出为 "2020/11/3"
    """
    try:
        dt = datetime.strptime(date_str, "%Y %b %d")
        formatted_date = f"{dt.year}/{dt.month}/{dt.day}"
        return formatted_date
    except:
        return "000/00/00"  # https://pubmed.ncbi.nlm.nih.gov/34927601/  https://pubmed.ncbi.nlm.nih.gov/34413851/

