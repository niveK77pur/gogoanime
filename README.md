# Installation

## Install Python dependencies

The dependencies are managed using [pipenv](https://pypi.org/project/pipenv/). Check <https://realpython.com/pipenv-guide/> for a nice introduction to the tool.

```python
pipenv install
```

## Install System dependencies

Since we are relying on [selenium] to extract the links, you also need to install the corresponding drivers and browsers. On KDE Neon (which is based on Ubuntu) you can do as follows.

```bash
# apt install firefox firefox-geckodriver
```

# Using the script



Extract MP4 video file links from 'www.gogoanime.so'
(or wheverever this points to)

Please also check the following section "About the implementation".

Usage:
    ./gogoanime.py <search term>

The links will be saved to a file in a corresponding folder. Downloading should
be taken care of outside of this program. NOTE: the links file is structured
for usage with the Aria2 downloading utility.

Example:
Note that the search term does not need to be quoted. The following would be
valid and equivalent queries:
    ./gogoanime.py yahari ore
    ./gogoanime.py "yahari ore"


# About the implementation

Accessing the download page (when pressing the yellow download button on an
episode on gogoanime) requires you to first complete a CAPTCHA verification.
Circumventing this verification is achieved by setting the 'User-Agent' and
the 'cf_clearance' cookie in the corresponding GET requests.

!! THAT SAID YOU NEED TO CHANGE/UPDATE THE COOKIE IF THE CAPTCHA IS TRIGGERED.

The first section in this code, called "Parameters", found after the imports,
presents two dictionaries that you can and may have to tweak. They are called
'headers' and 'cookies'.

The CAPTCHA may also be triggered due to something other than invalid cookies
(i.e. invalid User-Agent).  Please inspect the GET request to the download page
(yellow button) in your browser and check which parameters and cookies are
being set. Update the dictionaries at the top of this script accordingly.

You can check this information by using the Developer Tools in your browser
(F12 in FireFox). Navigate to the "Network" tab and refresh the page (F5). The
first request should be a GET request to 'streamani.net/download'. Look in the
Response and Request Headers for Cookies and other relevant information (i.e.
User-Agent).


# About downloading

For downloading with Aria2:
    Once you have extracted the links with this script, you can run the
    following command. NOTE: you should be inside the directory where the
    links are stored.

    # aria2c -i links.txt -c -x12 -s12 -k10M --max-overall-download-limit=3M
    
    Flags are as follows:
        -i  --input-file                    Where the URLs are stored
        -c  --continue                      Resume on partially downloaded files
        -x  --max-connection-per-server     Default is 1
        -s  --split                         Number of parallel downloads for item
        -k  --min-split-size                Split download of item into multiple ranges
        --max-overall-download-limit        Limit overall download speed


Last updated: Jul 16 2021
