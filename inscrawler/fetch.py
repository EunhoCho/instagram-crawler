import re


def get_parsed_hashtags(raw_text):
    regex = re.compile(r"#(\w+)")
    regex.findall(raw_text)
    return regex.findall(raw_text)


def fetch_hashtags(raw_test, dict_obj):
    hashtags = get_parsed_hashtags(raw_test)
    if hashtags:
        if "hashtags" in dict_obj.keys():
            dict_obj["hashtags"] = list(dict.fromkeys(dict_obj["hashtags"] + hashtags))
        else:
            dict_obj["hashtags"] = hashtags


def fetch_datetime(browser, dict_post):
    ele_datetime = browser.find_one(".eo2As .c-Yi7 ._1o9PC")
    datetime = ele_datetime.get_attribute("datetime")
    dict_post["datetime"] = datetime


def fetch_caption(browser, dict_post):
    ele_comments = browser.find(".eo2As .gElp9")

    if len(ele_comments) > 0:
        temp_element = browser.find("span", ele_comments[0])
        for element in temp_element:
            if element.text not in ['Verified', ''] and 'author' not in dict_post:
                dict_post["author"] = element.text
            elif element.text not in ['Verified', ''] and 'caption' not in dict_post:
                dict_post["caption"] = element.text
        fetch_hashtags(dict_post.get("caption", ""), dict_post)


def fetch_location(browser, dict_post):
    location = browser.find_one("a.O4GlU")
    if location:
        dict_post["location"] = location.text
