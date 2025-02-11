


import requests
from lxml import etree


# def deal_str(text):
#     return text.replace('\r', '').replace('\n', '').replace('\t', '') if text else ''

def deal_str(content_str):
    """
    summary: 处理换\r\n\t
    """
    if content_str:
        return content_str.strip().replace('\r', '').replace('\n', '').replace('\t', '') if content_str else ''
    else:
        return ''

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}
url = "https://pubmed.ncbi.nlm.nih.gov/39634198/"
res = requests.get(url, headers=headers)
response = etree.HTML(res.text)
a = ''.join(response.xpath('//div[@id="full-view-heading"]/div[@class="article-citation"]/span[@class="secondary-date"]/text()')).replace('Epub ', '').replace('.', '').strip()
b = deal_str(''.join(response.xpath('//h1[@class="heading-title"]/text()')[0]))  # https://pubmed.ncbi.nlm.nih.gov/39341996/
c= deal_str(''.join(response.xpath('//ul[@id="full-view-identifiers"]//span[@class="identifier doi"]/a/text()')))
print('a', a)
print('b', b)
print('c', c)