from bs4 import BeautifulSoup
import requests
from time import sleep
import re


def get_unified_url(href: str):  # unified_url for output: https://www.amazon.co.uk/dp/XXXXXXXXXX?m=YYYYYYYYYYYYYY
    matches = re.search(".*asin=(.+?)&.*seller=(.*)", href)
    if matches is None:
        unified_url = None
    else:
        asin = matches.group(1)
        seller = matches.group(2)
        unified_url = "https://www.amazon.co.uk/dp/{asin}?m={seller}".format(asin=asin, seller=seller)
    return unified_url


def sellers_page_process(all_sellers_url: str, headers: dict):  # process page with
    sleep(3)
    sellers_url_list = []
    all_sellers_page_soup = BeautifulSoup(requests.get(all_sellers_url, headers=headers).content, features="lxml")
    seller_divs = all_sellers_page_soup.find_all("div", {"class": "a-row a-spacing-mini olpOffer"})
    for seller_div in seller_divs:
        sellers_url_list.append(get_unified_url(seller_div.a.attrs["href"]))

    prev_next_buttons_divs = all_sellers_page_soup.find_all("div", {"class": "a-text-center a-spacing-large"})
    if prev_next_buttons_divs:
        last_li = prev_next_buttons_divs[0].ul.find_all("li")[-1]
        if last_li and "a-disabled" in last_li.attrs["class"]:
            next_page_url = None
        else:
            next_page_url = "https://www.amazon.co.uk{}".format(
                last_li.a.attrs["href"])
    else:
        next_page_url = None
    return next_page_url, sellers_url_list


def product_process(main_product_url: str, headers: dict) -> dict:  # main product page process
    response = requests.get(main_product_url, headers=headers)
    answer = {"response_status_code": response.status_code}
    if response.status_code == 200:
        page_soup = BeautifulSoup(response.content, features="lxml")
        other_sellers_link_divs = page_soup.find_all("div", {"id": "olp_feature_div", "class": "feature"})
        if other_sellers_link_divs and other_sellers_link_divs[0].a:
            all_sellers_url = "https://www.amazon.co.uk{}".format(other_sellers_link_divs[0].a.attrs["href"])
            answer["output"] = []
            while all_sellers_url:
                all_sellers_url, sellers_url_list = sellers_page_process(all_sellers_url, headers)
                answer["output"] += sellers_url_list
        else:
            answer["output"] = "Can't find sellers page"
    return answer


if __name__ == "__main__":
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    main_product_url = "https://www.amazon.co.uk/AMD-Ryzen-3900X-Processor-Cache/dp/B07SXMZLP9/"
    answer = product_process(main_product_url=main_product_url, headers=headers)
