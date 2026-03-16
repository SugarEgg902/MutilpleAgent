import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List

AMAZON_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "upgrade-insecure-requests": "1",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "connection": "keep-alive",
    "referer": "https://www.amazon.com/"
}


def search_amazon(product_name: str, max_results: int = 5) -> List[Dict[str, str]]:
    """搜索亚马逊商品，返回商品标题和价格列表"""
    url = "https://www.amazon.com/s"
    params = {
        "k": product_name,
        "__mk_zh_CN": "亚马逊网站",
    }

    session = requests.Session()
    res = session.get(url, headers=AMAZON_HEADERS, params=params, timeout=15)
    soup = BeautifulSoup(res.text, "lxml")

    items = soup.select('[data-component-type="s-search-result"]')
    products = []

    for item in items[:max_results]:
        title_el = item.select_one("h2 span")
        price_el = item.select_one(".a-price .a-offscreen")
        rating_el = item.select_one(".a-icon-alt")
        review_count_el = item.select_one(".a-size-base.s-underline-text")

        product = {}
        if title_el:
            product["title"] = title_el.text.strip()
        if price_el:
            product["price"] = price_el.text.strip()
        if rating_el:
            product["rating"] = rating_el.text.strip()
        if review_count_el:
            product["review_count"] = review_count_el.text.strip()

        if product.get("title"):
            products.append(product)

    return products
