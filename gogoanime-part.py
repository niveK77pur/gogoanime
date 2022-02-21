#!/usr/bin/env python

from selenium import webdriver
#  from seleniumwire import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

timeout = 20    # amount of seconds
####url = "https://gogoplay.io/download?id=MTUwNTA4&typesub=Gogoanime-SUB&title=Kaifuku+Jutsushi+no+Yarinaoshi+%28Uncensored%29+Episode+1"
filepath1 = "/tmp/f1.html"
filepath2 = "/tmp/f2.html"

firefox_options = FirefoxOptions()
#  firefox_options.add_argument("--headless")
firefox_options.add_argument("--private-window")

browser = webdriver.Firefox(options = firefox_options)

def get_html(url, filepath):
    print(url)
    try:
        browser.get(url)
        agent = browser.execute_script("return navigator.userAgent")
        print(agent)

        input("Press enter")
        what_is_this = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//body/section" + "/div" * 6 + "/a")
            )
        )
    except TimeoutException as error:
        print(error)

    with open(filepath, "w") as f:
        f.write(browser.page_source)

#  get_html("https://gogoplay.io/download?id=MTgwMDI1&typesub=Gogoanime-SUB&title=Sasaki+to+Miyano+Episode+5", filepath2)
#  get_html("https://gogoplay.io/download?id=MTgwMDMw&typesub=Gogoanime-SUB&title=Dragon%E2%80%99s+Disciple+Episode+4", filepath2)
get_html("https://gogoplay.io/download?id=MTUwNTA4&typesub=Gogoanime-SUB&title=Kaifuku+Jutsushi+no+Yarinaoshi+%28Uncensored%29+Episode+1", filepath2)

browser.quit()
