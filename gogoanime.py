#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

import sys
import re
import os

from selenium import webdriver
# use 'selenium-wire' package to modify headers
#  from seleniumwire import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if not __name__ == '__main__':
    print("Program must be run by itself. Exiting.")
    sys.exit(-1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                         Parameters (TO BE SET BY YOU)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#  Headers and Cookies for streamani/vidstream download page -------------------
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0',
}
cookies = {
    #  'cf_clearance': 'a8e8039fcefafd6a515195186980c54399b80c4f-1626262802-0-250',
    #  'prefetchAd_4732994': 'true',
    #  'prefetchAd_3386133': 'true',
}

# Download Location ------------------------------------------------------------
download_folder = os.environ["HOME"] + '/Videos/Anime'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                    Set-up
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#  Functions -------------------------------------------------------------------
def getSoup(session, url, headers=headers, cookies={}):
    response = session.get(url, headers=headers, cookies=cookies)
    return BeautifulSoup(response.text, "html.parser")

def getDownloadPageHTML(browser, url):
    """Use selenium to render the download page. This will reveal the download links"""
    try:
        timeout = 15
        browser.get(url)
        what_is_this = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//body/section" + "/div" * 6 + "/a")
            )
        )
        return BeautifulSoup(browser.page_source, "html.parser")
    except TimeoutException as error:
        print("Could not extract HTML for the following site. Timeout reached.")
        print(url)
        raise

#  Root URL of gogoanime -------------------------------------------------------
ROOT_URL = "https://gogoanime.so"

#  Set up some variables -------------------------------------------------------
episodes = {
    'gogoanime' : [],
    'vidstream' : [],
    'mp4': [],
}

s = requests.Session()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                Anime Selection
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#  Get list of animes to chose from --------------------------------------------
query = f'{ROOT_URL}/search.html?keyword=' + "+".join(sys.argv[1:])
soup = getSoup(s, query)

# Get list of animes that were found -------------------------------------------
anime_list = []
ul = soup.find('ul', class_='items')
for lst,rls in zip(ul.find_all('p', class_='name'), ul.find_all('p', class_='released')):
    link = ROOT_URL + lst.find('a').get('href')
    name = lst.find('a').get('title')
    year_text = re.search(r'\d+', rls.text)
    year = year_text.group() if year_text else "n/a"
    anime_list.append((name, link, year))
if not anime_list:
    print("No anime was found with keyword: '{}'".format(" ".join(sys.argv[1:])))
    print("Exiting.")
    sys.exit(1)

# Query user to pick an anime --------------------------------------------------
for i, (name, _, year) in enumerate(anime_list):
    print("{:5} | {} ({})".format(i,name,year))
while True:
    try:
        choice = int(input("Select anime (enter number): "))
        if choice < 0:
            print(">>> Aborting.")
            sys.exit()
        elif not choice < len(anime_list):
            print(">>> Invalid anime specified.")
            continue
        break
    except ValueError:
        print(">>> Choice must be an integer.")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                          Get GogoAnime Episode links
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print('Extracting GogoAnime episode links ...')

url, year = anime_list[choice][1:]
soup = getSoup(s, url)

ep_start = int(soup.find('a', class_='active').get('ep_start'))
ep_end = int(soup.find('a', class_='active').get('ep_end'))

folder = '{}/{}-{}'.format(download_folder, re.search(r'[\w-]+$', url).group(), year)
links_file = f'{folder}/links.txt'
if os.path.exists(links_file):
    with open(links_file, 'r') as f:
        links_file_contents = f.read()
    # extract existing episode numbers (tightly linked to how file is written/formatted)
    links_file_episodes = list(map(int, re.findall(r'out=.*ep(\d+).*?\n', links_file_contents)))
else:
    links_file_episodes = []

for ep in range(ep_start, ep_end):
    if ep+1 in links_file_episodes:
        continue # do not include existing episodes
    episodes['gogoanime'].append(re.sub(r'category/(.+)', r'\1-episode-'+str(ep+1), url))
if len(episodes['gogoanime']) == 0:
    print("No missing episodes to download. Exiting.")
    sys.exit(0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                  Get streamani/vidstream download page links
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print('Extracting download page links ...')

# from the yellow download button
for episode in episodes['gogoanime']:
    max_retries = 1
    for try_count in range(max_retries+1):
        # if the constructed gogoanime episode link contains no download
        # button (i.e. 404 page not found), retry with a variant of the link
        try:
            gogosoup = getSoup(s, episode)
            link = gogosoup.find('li', class_='dowloads').find('a').get('href')
        except AttributeError:
            if try_count > max_retries:
                # if all possibilities are exhausted, raise the error for
                # manual inspection
                raise
            # a field that appears at a 404 page
            entry_title = gogosoup.find(class_='entry-title')
            # 1st attempt: 2nd-season -> season-2, 23rd-season -> season-23
            if try_count == 0 and entry_title and entry_title.text == '404':
                episode = re.sub(r'(\d+)..-season', r'season-\1', episode)
            else:
                raise
            # more attempts to be added in the future if needed; update
            # 'max_retries' variable according to the number of tries
        else:
            break
    name = re.search(r'[\w-]+$', episode).group()
    # change "episode-x" to "ep00x" (add leading 0s for fixed width numbers)
    name = re.sub(r'episode-(\d+)$', lambda m: 'ep{:>03}'.format(m.group(1)), name)
    episodes['vidstream'].append((name,link))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                    Access download page and get mp4 links
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Selenium set-up --------------------------------------------------------------
print("Setting up selenium FireFox browser ...")

firefox_options = FirefoxOptions()
firefox_options.add_argument("--headless")
firefox_options.add_argument("--private-window")

browser = webdriver.Firefox(options = firefox_options)

# Get download links -----------------------------------------------------------
print('Extracting video links ...')

for n,episode in episodes['vidstream']:
    #  soup = getSoup(s, episode, headers=headers, cookies=cookies)
    soup = getDownloadPageHTML(browser, episode)
    # find link with highest resolution
    links = soup.find_all('div', class_='dowload')
    # filter out links without a resolution (i.e. has to contain 360P)
    links_episodes = [ l for l in links if re.search("[0-9]+P", l.text) ]
    if len(links_episodes) == 0:
        print('Something went wrong, no download links found.')
        debug_html = "/tmp/gogoanime.html"
        with open(debug_html, 'w') as f:
            f.write(str(soup))
        print(f'Page written to {debug_html} for debugging.')
        sys.exit(2)
    # sort according to resolution text
    link_maxres = sorted(links_episodes,
            key=(lambda l: re.search(r"([0-9]+)P", l.text).group(1))
            )[0]
    link = link_maxres.find('a').get('href')
    resolution = re.search(r"[0-9]+P", link_maxres.text).group()
    name = f"{n}_{resolution}.mp4"
    episodes['mp4'].append((name,link,episode))

browser.quit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                              Write links to file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create download directory (if non-existant) ----------------------------------
os.makedirs(folder, exist_ok=True)

# Write links to file ----------------------------------------------------------
with open(links_file, 'a') as f:
    f.write('\n'.join([ f'{link}\n    out={name}\n    referer={episode}'
        for name,link,episode in episodes['mp4']]))
    print(f"Links written to:\n   {links_file}")
