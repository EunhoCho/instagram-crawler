# Instagram Crawler

This program is for getting Instagram hashtag data, and location data without using Instagram API.

This crawler could fail due to updates on instagram’s website. If you encounter any problems, please contact me.

## Install
1. Make sure you have Chrome browser installed.
2. Download [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/) and put it into bin folder: `./inscrawler/bin/chromedriver`
3. Install Selenium: `pip3 install -r requirements.txt`

## User Auth
1. Make `inscrawler/secret.py` file.
2. Set the `username` and `password` variables' value to the ones corresponding to your Instagram account.
````
username = 'my_ig_username'
password = '***********'
````