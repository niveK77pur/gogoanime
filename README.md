# ⚠️ Archived ⚠️

As the commit history indicates, this project has been abandoned for quite a while.
More information on why can be found in [this comment](https://github.com/niveK77pur/gogoanime/issues/11#issuecomment-1690119772). Long story short, circumventing CAPTCHA on gogoanime was becoming more and more tricky, until it eventually surpassed my expertise.

Assuming you came here looking for a simple and nice download utility, I have personally moved on to [ani-cli](https://github.com/pystardust/ani-cli) which has been working great so I can highly recommend it! It does everything I intended this script to do at the core, and has many more neat features!

# About

This script extracts the MP4 video file links for episodes found on <www.gogoanime.so> (or wheverever this points to). All episodes for a whole season are automatically extracted. Usage is basically as follows; no quotes must be used here, check [Using the script](#using-the-script) further down for more details.

```bash
./gogoanime.py <search term>
```

Important to note is that the links are meant to be downloaded using [aria2](https://aria2.github.io/). Reason being that the links by themselves do not allow to download the episode; you also need to specify the `referer` request parameter. Plus, with aria2 we can neatly name our downloaded files. Recommended usage is as follows (command can be copy-pasted), more relevant flags can be found further down in section [About downloading](#about-downloading).

```bash
aria2c -i links.txt -c --auto-file-renaming false
```

# Installation

## Install Python dependencies

The dependencies are managed using [pipenv](https://pypi.org/project/pipenv/). Check <https://realpython.com/pipenv-guide/> for a nice introduction to the tool. Use the first command to install the packages in a new virtual environment. Use the second variant to install the packages globally on your system. The installation method **has an impact** on how you actually run the code. The latter might be the preferred way for the end user.

```python
pipenv install
pipenv install --system
```

## Install System dependencies

Since we are relying on [selenium](https://pypi.org/project/selenium/) to extract the links, you also need to install the corresponding browser and driver. We use [Firefox](https://www.mozilla.org/firefox/) here, for which you need the [GeckoDriver](https://github.com/mozilla/geckodriver).

On KDE Neon (which is based on Ubuntu) you can install them as follows.

```bash
# apt install firefox firefox-geckodriver
```

# Using the script

The links will be saved to a file in a corresponding folder located inside of `$HOME/Videos/Anime`. The download location can be changed by modifying the `download_folder` variable in the code. The script further tries to grab the highest resolution video found in the download page. Downloading should be taken care of **outside of this program**. To be noted is that the links file is structured for usage with the [aria2](https://aria2.github.io/) downloading utility.

## Usage

```bash
./gogoanime.py <search term>
```

Upon hitting enter, the script will parse the gogoanime page for results given the search term and you will be prompted to select one by typing the number attributed to the entry. Entering a negative number will abort and exit the script. Alternatively ctrl+c also does the job.

## Example

Note that the *search term* **must not** be quoted. Internally, all command linke arguments will be concatenated which should make it less of a hassle to look for animes.

```bash
./gogoanime.py yahari ore
```


# About downloading

Once you have extracted the links with this script, you can run the following command. Note that you should be inside the directory where the links are stored, which by default is always a file called `links.txt`.

````bash
aria2c -i links.txt
````

To resume partially downloaded files use the `-c` or `--continue` flag.

```bash
aria2c -i links.txt -c
```

It may be preferred to use the following instead however, as aria2 by default downloads existing files again but simply renames them by adding a number. With the additional flag we tell aria to not rename existing files, which will cause aria2 to skip the download since by default files are not overwritten (see `--allow-overwrite` flag for aria2c).

```bash
aria2c -i links.txt -c --auto-file-renaming false
```

This last form is the most robust, since partially downloaded episodes will resume their download. At the same time, already downloaded episodes will not be re-downloaded or overwritten.

## Fine tuning the download process

These commands are already plenty to download the episodes. However, aria2 has many options and the following flags are a relevant collection which allow to fine tune the downloading further if needed.

```bash
aria2c -i links.txt -c -x12 -s12 -k10M --auto-file-renaming false --max-overall-download-limit=3M
```
Flags are as follows:

| Short | Long | Description |
| ----- | ---- | ----------- |
| -i | --input-file                | File in which the URLs are stored |
| -c | --continue                  | Resume on partially downloaded files |
| -x | --max-connection-per-server | Default is 1 |
| -s | --split                     | Number of parallel downloads for item |
| -k | --min-split-size            | Split download of item into multiple ranges |
| | --auto-file-renaming           | Rename file if the same file already exists |
| | --max-overall-download-limit   | Limit overall download speed |


# About the implementation

Accessing the download page (when pressing the yellow download button on an episode on gogoanime) requires you to first complete a CAPTCHA verification. Circumventing this verification is seemingly only achievable by rendering the page with a browser (as it does not require any human intervention). For this reason, selenium is used allowing us to render the page in a headless browser and then to extract the download links. This is an automated process of course.

The first section in this code, called "Parameters", found after the imports, presents two dictionaries that you can and may have to tweak. They are called 'headers' and 'cookies'. The `User-Agent` header is important to set, because otherwise Python's request will be shut down due to being a bot. In elder versions of gogoanime, cookies were needed to enter the download page containing the video links. At this point in time, the cookies are not used anywhere in the code.

<!--
The CAPTCHA may also be triggered due to something other than invalid cookies (i.e. invalid User-Agent).  Please inspect the GET request to the download page (yellow button) in your browser and check which parameters and cookies are being set. Update the dictionaries at the top of this script accordingly.  You can check this information by using the Developer Tools in your browser (F12 in FireFox). Navigate to the "Network" tab and refresh the page (F5). The first request should be a GET request to 'streamani.net/download'. Look in the Response and Request Headers for Cookies and other relevant information (i.e.  User-Agent).
-->
