import time
import pandas
import json

# from types import coroutine
from selenium import webdriver
from urllib.parse import urlparse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchElementException,
)

service = Service(r"C:\Program Files\chromedriver-win64\chromedriver.exe")
options = Options()
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://open.spotify.com")

with open(
    r"C:\All apps\Visual Studio Code\Python\Spotify Scraper\spotify_cookies.json", "r"
) as f:
    cookies = json.load(f)

for cookie in cookies:
    cookie.pop("sameSite", None)
    driver.add_cookie(cookie)

driver.get("https://open.spotify.com/collection/tracks")

input("wait for Spotify to load then hit enter in console...")

results = {"track_name": [], "url": [], "track_id": []}


def get_track_id(url):
    parsed_url = urlparse(url)
    track_id = parsed_url.path.split("/")[-1]
    return track_id


def isduplicate(track_id):
    if track_id in results["track_id"]:
        return True
    return False


def scrape_visible_rows():
    rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"]')
    for row in rows:
        try:
            # get url
            link_elements = row.find_elements(By.CSS_SELECTOR, 'a[href*="/track/"]')
            if not link_elements:
                continue
            url = link_elements[0].get_attribute("href")

            # get track id
            track_id = get_track_id(url)

            # deduplicate
            if isduplicate(track_id):
                continue

            # get track name
            name_elements = row.find_elements(By.XPATH, ".//div[2]/div/a/div")
            if not name_elements:
                continue
            track_name = name_elements[0].text

        except (NoSuchElementException, StaleElementReferenceException):
            continue

        # append results
        results["track_name"].append(track_name)
        results["url"].append(url)
        results["track_id"].append(track_id)


def scroll():
    driver.execute_script(
        """const rows = document.querySelectorAll("[data-testid*='tracklist-row']");
        rows[rows.length - 2]?.scrollIntoView({ behavior: 'auto', block: 'end' });"""
    )


def main():
    data_testid_tl = driver.find_element(By.CSS_SELECTOR, '[data-testid="track-list"]')
    row_count = data_testid_tl.get_attribute("aria-rowcount")
    print(row_count)
    n = 0
    while n <= 5:
        rows_last = driver.find_elements(
            By.CSS_SELECTOR, "[data-testid*='tracklist-row']"
        )
        scrape_visible_rows()
        scroll()
        rows_now = driver.find_elements(
            By.CSS_SELECTOR, "[data-testid*='tracklist-row']"
        )
        if rows_last == rows_now:
            n += 1
        else:
            n = 0
        time.sleep(0.25)


main()

input("press enter to get track table")

track_table = pandas.DataFrame(
    {"track_name": results["track_name"], "url": results["url"]}
)
track_table.to_csv(
    r"C:\All apps\Visual Studio Code\Python\Spotify Scraper\track_table.csv"
)
pandas.set_option("display.max_rows", None)
print(track_table)


# ".//div[2]/div/a/div"
