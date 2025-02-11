from lxml import etree
from loguru import logger as log
from utils.public_func import *


def parse_list_page(list_resp_text):
    article_etree = etree.HTML(list_resp_text)
    article_detail_urls = [f"https://pubmed.ncbi.nlm.nih.gov{detail_id}" for detail_id in article_etree.xpath('//div[@class="docsum-wrap"]/div[@class="docsum-content"]/a/@href')]
    return article_detail_urls


def parse_detail_page(detail_resp_text, detail_url):
    response = etree.HTML(detail_resp_text)
    item = {}
    item["pm_ID"] = deal_str(''.join(response.xpath('//ul[@id="full-view-identifiers"]//strong[@class="current-id" and @title="PubMed ID"]/text()')))
    item["article_title"] = deal_str(''.join(response.xpath('//h1[@class="heading-title"]/text()')))  # https://pubmed.ncbi.nlm.nih.gov/39341996/
    item["article_doi"] = deal_str(''.join(response.xpath('//ul[@id="full-view-identifiers"]//span[@class="identifier doi"]/a/text()')))
    item["pub_time"] = deal_pub_time(deal_str(''.join(response.xpath('//div[@id="full-view-heading"]/div[@class="article-citation"]/span[@class="secondary-date"]/text()')).replace('Epub ', '').replace('.', '').strip()))
    item["magazine_name"] = deal_str(''.join(response.xpath('//meta[@name="citation_publisher"]/@content')))
    # 作者及所属关系（作者 || 所属机构） https://pubmed.ncbi.nlm.nih.gov/39924477/ 多个
    authors_infos = response.xpath('//div[@class="inline-authors"]/div[@class="authors"]/div[@class="authors-list"]/span[contains(@class,"authors-list-item")]')
    processed_authors_infos_l = []
    for authors_info in authors_infos:
        name = ''.join(authors_info.xpath('.//a[@class="full-name"]/text()'))
        aff_nums = authors_info.xpath('.//sup[@class="affiliation-links"]/a[@class="affiliation-link"]/text()')
        if aff_nums:
            processed_authors_infos_l.append(
                f"{deal_str(name)}@{','.join(deal_str(aff_num) for aff_num in aff_nums)}"
            )
    affiliations = response.xpath('//ul[@class="item-list"]/li')
    aff_dict = {}
    for li in affiliations:
        number = deal_str(''.join(li.xpath('.//sup[@class="key"]/text()')))
        if number:
            affiliation_text = deal_str(''.join(li.xpath(f'normalize-space(substring-after(., "{number}"))')))
            aff_dict[number] = affiliation_text
    authors_with_affiliations = ''.join(
        [
            f"{author.split('@')[0]} || " + ' | '.join(
                [aff_dict.get(aff_num.strip()) for aff_num in author.split('@')[1].split(',')]
            ) + "\n\n"
            for author in processed_authors_infos_l
        ]
    )
    item["authors_with_affiliations"] = authors_with_affiliations
    # 摘要内容（abstract）
    abstract_content_p_xp = response.xpath('//div[@id="eng-abstract"]/p')
    al_abstract_text = []
    for xp in abstract_content_p_xp:
        full_text = ''.join(xp.xpath('normalize-space(string(.))'))
        al_abstract_text.append(full_text)
    abstract_content = "\n\n".join(al_abstract_text)
    item["abstract_content"] = abstract_content
    item["article_url"] = detail_url

    return item