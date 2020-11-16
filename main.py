from multiprocessing.pool import Pool

import requests
from bs4 import BeautifulSoup

import crawler
import json


def crawl_info(item):
    path = item['key']
    req = requests.get(path)

    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    hashtag_elements = soup.find_all('meta', attrs={'property': 'instapp:hashtags'})

    result = {'key': path}

    tags = []
    for element in hashtag_elements:
        tags.append(element['content'])
    if len(tags) > 0:
        result['hashtags'] = tags

    content_element = json.loads(soup.find('script', attrs={'type': 'application/ld+json'}).contents[0])

    if 'contentLocation' in content_element.keys():
        result['location'] = content_element['contentLocation']['name']

    return result

if __name__ == "__main__":
    result = crawler.get_posts_by_hashtag('제주', 10, False)
    # result = [{'key': 'https://www.instagram.com/p/CHnQJaKMr-P/?hl=ko'}]
    crawler.output(result, 'output.json')

    cores = 4
    with Pool(cores) as pool:
        results = pool.map(crawl_info, result)
        pool.close()
        pool.join()

        crawler.output(results, "./output.json")

        hashtags = []
        locations = []

        for item in results[:]:
            if 'hashtags' in item.keys():
                hashtags.append(item)
            if 'location' in item.keys():
                locations.append(item)

        crawler.output(hashtags, "./hashtags.json")
        crawler.output(locations, "./locations.json")
