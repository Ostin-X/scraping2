# import json
# import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_business_number_of_reviews(business_item):
    # business_number_of_reviews = business_item.find(class_='css-chan6m').text.split(' ')[0][1:]
    try:
        business_number_of_reviews = business_item.find(class_='css-chan6m').text
        if 'review' not in business_number_of_reviews:
            raise AttributeError
    except AttributeError:
        business_number_of_reviews = business_item.find(class_='css-8xcil9').text

    business_number_of_reviews = business_number_of_reviews.split(' ')[0][1:]
    if business_number_of_reviews[-1] == 'k':
        business_number_of_reviews = int(float(business_number_of_reviews[:-1]) * 1000)
    else:
        business_number_of_reviews = int(business_number_of_reviews)
    return business_number_of_reviews


def get_selenium_page(business_yelp_url):
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.get(business_yelp_url)
    driver.execute_script("window.scrollBy(0,2200)", "")
    time.sleep(2)
    resp_text = driver.page_source
    return resp_text


def get_reviews(src_page_text, reviews_count):
    soup_business = BeautifulSoup(src_page_text, 'lxml')

    reviews_list = []
    try:
        business_url = soup_business.find(text='Business website').find_next(class_='css-1p9ibgf').find('a', class_='css-1idmmu3').text
        # business_url = soup_business.find(class_='css-ncv51b').find(class_='css-xp8w2v').find('a', class_='css-1idmmu3').text
        if '.' not in business_url:
            raise AttributeError
    except AttributeError:
        business_url = 'None'
    reviews = soup_business.find(id='reviews').find(class_='list__09f24__ynIEd').find_all('li')
    for item in reviews:
        name = item.find(class_='css-19v1rkv').text
        link = f'https://www.yelp.com{item.find(class_="css-vzslx5")["href"]}'
        user_location = item.find(class_='css-qgunke').text
        if len(user_location) > 100:
            user_location = 'None'
        date = item.find(class_='css-chan6m').text
        reviews_list.append({
            'Name': name,
            'Location': user_location,
            'Date': date,
            'Yelp Url': link,
        })
        if (reviews_count := reviews_count - 1) == 0:
            break
    return business_url, reviews_list

    # data_review = re.findall(r'"review":(\[.*?])', src_business)
    # try:
    #     reviews = json.loads(data_review[0])
    # except json.decoder.JSONDecodeError:
    #     pass
    # else:
    #
    #
    #     for jsn in reviews:
    #
    #         reviewer_name = jsn['author']
    #         reviewer_location = jsn['reviewRating']
    #         reviewer_date = jsn['datePublished']
    #         reviews_list.append({
    #             'Name': reviewer_name,
    #             'Location': reviewer_location,
    #             'Date': reviewer_date
    #         })
    #         if (reviews_count := reviews_count - 1) == 0:
    #             break
    # return business_url, reviews_list

#
# business_name = 'San Tung'
# location = 'San Francisco, CA'
#
# with open(f'data/businesses/{business_name}-{location}.html', 'r', encoding='utf-8-sig') as file:
#     src_business = file.read()
#
# if __name__ == '__main__':
#     print(get_reviews(src_business, 5))
