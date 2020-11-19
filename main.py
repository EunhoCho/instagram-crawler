import argparse
import json
import multiprocessing
from datetime import datetime
from itertools import repeat
from multiprocessing.pool import Pool
from time import sleep

import numpy as np
from tqdm import tqdm

from inscrawler import InsCrawler


def usage():
    return """
        python main.py Jeju
        python main.py Jeju -n 100
        python main.py Jeju -n 100 --fetch_location
        python main.py Jeju -n 100 --fetch_location --fetch_comments
        
        The default number for fetching posts via hashtag is 100.
    """


def get_post_keys_by_hashtag(tag, number, debug):
    ins_crawler = InsCrawler(has_screen=debug)
    return ins_crawler.get_latest_posts_by_tag(tag, number)


def get_hashtags_by_post_key(post_key, debug, number):
    if len(post_key) == 0:
        return []

    ins_crawler = InsCrawler(has_screen=debug)
    result = []

    progress_bar = tqdm(total=len(post_key))
    progress_bar.set_description("fetching_2_" + str(number))
    for key in post_key:
        result.append(ins_crawler.fetch_post(key))
        progress_bar.update(1)

    return result


def output(data, filepath):
    out = json.dumps(data, ensure_ascii=False)
    if filepath:
        with open(filepath, "w", encoding="utf8") as f:
            f.write(out)
    else:
        print(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instagram Crawler", usage=usage())
    parser.add_argument("hashtag")
    parser.add_argument("-n", "--number", type=int, help="number of returned posts")
    parser.add_argument("--multi", action="store_true")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()
    now = datetime.now()

    # Crawl keys
    data = get_post_keys_by_hashtag(args.hashtag, args.number or 100, args.debug)
    output(data, './keys' + '_' + now.strftime("%Y%m%d_%H%M%S") + '.json')

    # Crawl hashtags
    results = []
    if args.multi:
        try:
            num_cores = multiprocessing.cpu_count()

            split_data = np.array_split(data, num_cores)
            split_data = [x.tolist() for x in split_data]

            with Pool(num_cores) as pool:
                result_lists = pool.starmap(get_hashtags_by_post_key,
                                            zip(split_data, repeat(args.debug), list(range(num_cores))))
                pool.close()
                pool.join()

                for result_list in result_lists:
                    results += result_list

        except Exception:
            sleep(10)
            results = get_hashtags_by_post_key(data, args.debug, 0)

    else:
        results = get_hashtags_by_post_key(data, args.debug, 0)

    output(results, './output' + '_' + now.strftime("%Y%m%d_%H%M%S") + '.json')

    hashtags = []
    locations = []

    for item in results[:]:
        if 'hashtags' in item.keys():
            hashtags.append(item)
        if 'location' in item.keys():
            locations.append(item)

    output(hashtags, './hashtags' + '_' + now.strftime("%Y%m%d_%H%M%S") + '.json')
    output(locations, './locations' + '_' + now.strftime("%Y%m%d_%H%M%S") + '.json')
