import json
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from ysp_funcs import get_reviews, get_business_number_of_reviews, get_selenium_page

category = 'Chinese Food'
# category = 'contractors'
location = 'San Francisco, CA'
# location = 'NY'

cat_quote = quote(category)
loc_quote = quote(location)
number_of_reviews_for_business = 5

headers = {
    'Accept': '*/*',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}

# get Category pages
page = 0
end_page = 5
while True:
    business_info_list = []
    url = f'https://www.yelp.com/search?find_desc={cat_quote}&find_loc={loc_quote}&start={page * 10}'
    req = requests.get(url, headers=headers)
    src = req.text
    if "We're sorry, the page of results you requested is unavailable." in src or page > end_page:
        break

    with open(f'data/pages/{category}-{location}-page-{page}.html', 'w', encoding='utf-8') as file:
        file.write(src)

    print(f'Page {page} saved')
    page += 1

    # Get info from index page
    # with open(f'data/pages/{category}-{location}-page-{0}.html', 'r', encoding='utf-8') as file:
    #     src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    business_info = soup.find_all(class_='container__09f24__mpR8_')

    for business_item in business_info:

        try:
            business_class = business_item.find(class_='css-19v1rkv')
            business_name = business_class.text
            business_yelp_url_before_redirect = business_class['href']

            if '/adredir' not in business_yelp_url_before_redirect:
                business_yelp_url = f'https://www.yelp.com{business_yelp_url_before_redirect.split("?")[0]}'

                business_rating = float(business_item.find(class_='css-gutk1c').text)
                resp_text = get_selenium_page(business_yelp_url)

                with open(f'data/businesses/{business_name}-{location}.html', 'w', encoding='utf-8') as file:
                    file.write(resp_text)

                business_number_of_reviews = get_business_number_of_reviews(business_item)
                business_url, reviews_list = get_reviews(resp_text, number_of_reviews_for_business)
                business_info_list.append({
                    'Name': business_name,
                    'Rating': business_rating,
                    'Number of reviews': business_number_of_reviews,
                    'Yelp URL': business_yelp_url,
                    'URL': business_url,
                    'Reviews': reviews_list
                })

        except Exception as e:
            print(business_name)
            raise e

        finally:
            with open(f'data/results/{category}-{location}-page-{page - 1}.json', 'w', encoding='utf-8-sig') as file:
                json.dump(business_info_list, file, indent=4, ensure_ascii=False)
