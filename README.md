# Scrapy Scraper

Web crawler and scraper based on Scrapy and Playwright's headless browser.

To use the headless browser specify `-p` option. Browsers, unlike other standard web request libraries, have the ability to render JavaScript encoded HTML content.

To automatically download and beautify all JavaScript files, including minified ones, specify `-dir downloads` option - where `downloads` is your desired output directory.

Resources:

* [scrapy.org](https://scrapy.org) (official)
* [playwright.dev](https://playwright.dev/python/docs/intro) (official)
* [scrapy/scrapy](https://github.com/scrapy/scrapy) (GitHub)
* [scrapy-plugins/scrapy-playwright](https://github.com/scrapy-plugins/scrapy-playwright) (GitHub)

Tested on Kali Linux v2023.4 (64-bit).

Made for educational purposes. I hope it will help!

## Table of Contents

* [How to Install](#how-to-install)
	* [Install Playwright and Chromium](#install-playwright-and-chromium)
	* [Standard Install](#standard-install)
	* [Build and Install From the Source](#build-and-install-from-the-source)
* [How to Run](#how-to-run)
* [Usage](#usage)
* [Images](#images)

## How to Install

### Install Playwright and Chromium

```bash
pip3 install --upgrade playwright

playwright install chromium
```

Make sure each time you upgrade your Playwright dependency to re-install Chromium; otherwise, you might get an error using the headless browser.

### Standard Install

```bash
pip3 install --upgrade scrapy-scraper
```

### Build and Install From the Source

```bash
git clone https://github.com/ivan-sincek/scrapy-scraper && cd scrapy-scraper

python3 -m pip install --upgrade build

python3 -m build

python3 -m pip install dist/scrapy-scraper-2.4-py3-none-any.whl
```

## How to Run

Restricted (domain whitelisting is on):

```fundamental
scrapy-scraper -u https://example.com/home -o results.txt -a random -s 2 -rs -dir js -l
```

Unrestricted (domain whitelisting is off):

```fundamental
scrapy-scraper -u https://example.com/home -o results.txt -a random -s 2 -rs -dir js -l -w off
```

## Usage

```fundamental
Scrapy Scraper v2.4 ( github.com/ivan-sincek/scrapy-scraper )

Usage:   scrapy-scraper -u urls                     -o out         [-dir directory]
Example: scrapy-scraper -u https://example.com/home -o results.txt [-dir downloads]

DESCRIPTION
    Crawl and scrape websites
URLS
    File with URLs or a single URL to start crawling and scraping from
    -u, --urls = urls.txt | https://example.com/home | etc.
WHITELIST
    File with whitelisted domains to limit the crawling scope
    Specify 'off' to disable domain whitelisting
    Default: domains extracted from the URLs
    -w, --whitelist = whitelist.txt | off | etc.
LINKS
    Include all links and sources (incl. 3rd party) in the output file
    -l, --links
PLAYWRIGHT
    Use Playwright's headless browser
    -p, --playwright
PLAYWRIGHT WAIT
    Wait time in seconds before fetching the content from the page
    Applies only if Playwright's headless browser is used
    -pw, --playwright-wait = 2 | 4 | etc.
CONCURRENT REQUESTS
    Number of concurrent requests
    Default: 30
    -cr, --concurrent-requests = 15 | 45 | etc.
CONCURRENT REQUESTS PER DOMAIN
    Number of concurrent requests per domain
    Default: 10
    -crd, --concurrent-requests-domain = 5 | 15 | etc.
SLEEP
    Sleep time in seconds between two consecutive requests to the same domain
    -s, --sleep = 1.5 | 3 | etc.
RANDOM SLEEP
    Randomize the sleep time on each request to vary between '0.5 * sleep' and '1.5 * sleep'
    -rs, --random-sleep
AUTO THROTTLE
    Auto throttle concurrent requests based on the load and latency
    Sleep time is still respected
    -at, --auto-throttle = 0.5 | 10 | 15 | 45 | etc.
RETRIES
    Number of retries per URL
    -rt, --retries = 2 | 4 | etc.
RECURSION
    Recursion depth limit
    Specify '0' for no limit
    Default: 1
    -r, --recursion = 0 | 2 | etc.
REQUEST TIMEOUT
    Request timeout in seconds
    Default: 60
    -t, --request-timeout = 30 | 90 | etc.
HEADER
    Specify any number of extra HTTP request headers
    -H, --header = "Authorization: Bearer ey..." | etc.
COOKIE
    Specify any number of extra HTTP cookies
    -b, --cookie = PHPSESSIONID=3301 | etc.
USER AGENT
    User agent to use
    Default: Scrapy Scraper/2.4
    -a, --user-agent = curl/3.30.1 | random[-all] | etc.
PROXY
    Web proxy to use
    -x, --proxy = http://127.0.0.1:8080 | etc.
DIRECTORY
    Output directory
    All extracted JavaScript files will be saved in this directory
    -dir, --directory = downloads | etc.
OUT
    Output file
    -o, --out = results.txt | etc.
DEBUG
    Debug output
    -dbg, --debug
```

## Images

<p align="center"><img src="https://github.com/ivan-sincek/scrapy-scraper/blob/main/img/scraping.png" alt="Scraping"></p>

<p align="center">Figure 1 - Scraping</p>
