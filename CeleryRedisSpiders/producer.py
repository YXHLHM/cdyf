import time
import copy
import math
from lxml import etree
from tasks import process_list_page
from loguru import logger as log
import datetime
import requests
from urllib.parse import unquote

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


def deal_str(content_str):
    """
    summary: 处理换\r\n\t
    """
    if content_str:
        return content_str.strip().replace('\r', '').replace('\n', '').replace('\t', '') if content_str else ''
    else:
        return ''


base_url = "https://pubmed.ncbi.nlm.nih.gov/"


def get_between_date(begin_date, end_date=None, date_format="%Y-%m-%d", **time_interval):
    """
    @summary: 获取一段时间间隔内的日期，默认为每一天
    ---------
    @param begin_date: 开始日期 str 如 2018-10-01
    @param end_date: 默认为今日
    @param date_format: 日期格式，应与begin_date的日期格式相对应
    @param time_interval: 时间间隔 默认一天 支持 days、seconds、microseconds、milliseconds、minutes、hours、weeks
    ---------
    @result: list 值为字符串
    """

    date_list = []

    begin_date = datetime.datetime.strptime(begin_date, date_format)
    end_date = (
        datetime.datetime.strptime(end_date, date_format)
        if end_date
        else datetime.datetime.strptime(
            time.strftime(date_format, time.localtime(time.time())), date_format
        )
    )
    time_interval = time_interval or dict(days=1)

    while begin_date <= end_date:
        date_str = begin_date.strftime(date_format)
        date_list.append(date_str)

        begin_date += datetime.timedelta(**time_interval)

    if end_date.strftime(date_format) not in date_list:
        date_list.append(end_date.strftime(date_format))

    return date_list


def get_all_page(params):
    resp = etree.HTML(requests.get(url=base_url, params=params).text)
    total_data = int(deal_str(resp.xpath('//div[@class="results-amount"]//span[@class="value"]/text()')[0]).replace(',', ''))
    return total_data, math.ceil(total_data / 10)



start_date_str = "2025/1/1"
end_date_str = "2025/2/10"
dates = get_between_date(start_date_str, end_date_str, date_format="%Y/%m/%d", days=15)
dates = dates + [dates[-1]]
# 按时间区间组合查询
box = []
for i in range(len(dates) - 1):
    start_date = dates[i]
    end_date = dates[i + 1]
    date_range = f"dates.{start_date}-{end_date}"
    params = {
        "term": "Lung Cancer",
        "filter": date_range,
    }
    total_data, total_pages = get_all_page(copy.deepcopy(params))
    # total_pages = 1
    log.info(f"{start_date} to {end_date} have {total_data} 条， {total_pages} 页")

    for p in range(1, total_pages + 1):
        box.append(
             f"https://pubmed.ncbi.nlm.nih.gov/?term=Lung Cancer&filter={date_range}&page={p}"
        )


def start_production():
    batch_size = 500  # 每批提交的任务数
    for i in range(0, len(box), batch_size):
        batch_urls = box[i:i + batch_size]
        for url in batch_urls:
            process_list_page.delay(url)
        log.success(f"提交了 {len(batch_urls)} 个任务")


if __name__ == "__main__":
    start_production()
