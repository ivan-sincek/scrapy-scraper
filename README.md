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

## How to Install

### Install Playwright and Chromium

```bash
pip3 install --upgrade playwright

playwright install chromium
```

Make sure each time you upgrade your Playwright dependency to re-install Chromium; otherwise, you might get no results if using the headless browser.

### Standard Install

```bash
pip3 install --upgrade scrapy-scraper
```

### Build and Install From the Source

```bash
git clone https://github.com/ivan-sincek/scrapy-scraper && cd scrapy-scraper

python3 -m pip install --upgrade build

python3 -m build

python3 -m pip install dist/scrapy-scraper-1.7-py3-none-any.whl
```

## How to Run

Restricted (domain whitelisting is on):

```fundamental
scrapy-scraper -u https://example.com/home -o results.txt -a random -s random -dir js -l
```

Unrestricted (domain whitelisting is off):

```fundamental
scrapy-scraper -u https://example.com/home -o results.txt -a random -s random -dir js -l -w off
```

## Usage

```fundamental
Scrapy Scraper v1.7 ( github.com/ivan-sincek/scrapy-scraper )

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
    Default: domains extracted from initial URLs
    -w, --whitelist = whitelist.txt | off | etc.
LINKS
    Include all links and sources (incl. 3rd party) in the output file
    -l, --links
PLAYWRIGHT
    Use Playwright's headless browser
    -p, --playwright
CONCURRENT REQUESTS
    Number of concurrent requests
    Default: 30
    -cr, --concurrent-requests = 15 | 45 | etc.
CONCURRENT REQUESTS PER DOMAIN
    Number of concurrent requests per domain
    Default: 10
    -crd, --concurrent-requests-domain = 5 | 15 | etc.
SLEEP
    Sleep time between two consecutive requests to the same domain
    Specify 'random' to sleep a random amount of time between 0.5 and 1.5 seconds
    Default: 1.5
    -s, --sleep = 0 | 2 | 4 | random | etc.
AUTO THROTTLE
    Auto throttle concurrent requests based on the load and latency
    -at, --auto-throttle = 0.5 | 10 | 15 | 45 | etc.
RECURSION
    Recursion depth limit
    Specify '0' for no limit
    Default: 1
    -r, --recursion = 0 | 2 | 4 | etc.
USER AGENT
    User agent to use
    Default: Scrapy Scraper/1.7
    -a, --user-agent = curl/3.30.1 | random | etc.
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
```
