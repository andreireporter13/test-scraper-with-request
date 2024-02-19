#
#
# Config for Dynamic Get Method -> For Json format!
#
# Company ---> Citygross
# Link ------> https://www.citygross.se/matvaror
#
# ------ IMPORTANT! ------
# if you need return soup object:
# you cand import from __utils -> GetHtmlSoup
# if you need return regex object:
# you cand import from __utils ->
# ---> get_data_with_regex(expression: str, object: str)
#
#
from __utils import (
    GetRequestJson,
    get_county,
    get_job_type,
    Item,
    UpdateAPI,

    #
    GetStaticSoup,
    get_data_with_regex,
)
import json


def hack_id_from_site_with_regex() -> str:
    '''
    ... get ids for get requests
    '''

    regex_data = str(GetStaticSoup('https://www.citygross.se/matvaror'))
    return get_data_with_regex('<script.*?src="https://cert\.tryggehandel\.net/(.*?)".*?>', regex_data).split()[-1].split("=")[-1][:-2]


# get id in one session
hacked_id = hack_id_from_site_with_regex()


def get_navigation_data_for_matvaror() -> tuple[str, dict]:
    '''
    ... get all navigation data for Matvaror
    '''

    matvaror_url = 'https://www.citygross.se/api/v1/navigation'

    matvaror_headers = {
        'Accept': 'application/json',
        'Referer': 'https://www.citygross.se/matvaror',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    return matvaror_url, matvaror_headers


def prepare_get_headers_per_category(id_store: str, page: str, slug_category: str) -> tuple[str, dict]:
    '''
    ... prepare get request for second json
    '''

    second_url = f'https://www.citygross.se/api/v1/esales/products?categoryId={id_store}&page={page}&size=24&store'

    second_headers = {
        'authority': 'www.citygross.se',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.6',
        'cookie': f'e_sk={hacked_id}',
        'referer': f'https://www.citygross.se/matvaror/{slug_category}?page={page}',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    return second_url, second_headers


def scraper() -> dict[list]:
    '''
    ... scrape data from Citygross scraper.
    '''

    # first headers type
    url1, headesr1 = get_navigation_data_for_matvaror()
    first_json_request = GetRequestJson(url=url1, custom_headers=headesr1)

    # store all data in one list
    store_data_products = dict()
    for slug_ in first_json_request.get('data').get('tree').get('children')[0].get('children'):

        id_cat = slug_.get('id')
        name_title = slug_.get('name')
        link_cat = slug_.get('link').get('url')
        if '---' not in name_title and 'test' not in link_cat:

            #make another request and collect all the data
            list_for_slug = list()
            page = 1
            count = 1
            flag = True
            while flag:

                # prepare new post requests
                url2, headers2 = prepare_get_headers_per_category(id_store=id_cat,
                                                                  page=str(page),
                                                                  slug_category=link_cat.split('/')[-1],
                                                                )
                
                # get dict per per request
                data_ = GetRequestJson(url=url2, custom_headers=headers2).get('data')
                
                if len(data_) > 0:

                    # scrape data
                    for product_data in data_:
                        list_for_slug.append({
                            "name": product_data.get("name"),
                            "brand_manufacturer": product_data.get('brand'),
                            "price": product_data.get('defaultPrice').get('currentPrice').get('price'),
                            "gtin": product_data.get('gtin'), 
                        })
                else:
                    flag = False

                print(f"Make get requests to slug {link_cat} and page {page}")
                # increment pages
                page += 1
                count += 1

            # store data in dict - key slug of category
            store_data_products.setdefault(link_cat.split('/')[-1], []).extend(list_for_slug)

            # here clear list
            list_for_slug.clear()

            # restore page for next slug
            page = 1

    return store_data_products


def main() -> None:
    '''
    ... all things here
    '''

    company_name = "Citygross"

    all_products = scraper()
    print(all_products, len(all_products))


if __name__ == '__main__':
    main()
