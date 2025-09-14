import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

service = Service(r"C:\Program Files\chromedriver-win64\chromedriver.exe")
options = Options()
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://open.spotify.com")

print("log in")
input("enter when loged in")

cookies = driver.get_cookies()
with open(r"C:\All apps\Visual Studio Code\Python\Spotify Scraper\spotify_cookies.json", "w") as f:
    json.dump(cookies, f)

print("cookies saved")
driver.quit()
