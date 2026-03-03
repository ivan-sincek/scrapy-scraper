# Scrapy Scraper

Web crawler and scraper based on Scrapy and Playwright's headless browser.

To use the headless browser specify `-p` option. Browsers, unlike other standard web request libraries, have the ability to render JavaScript encoded HTML content.

Future plans:

* check if Playwright's Chromium headless browser is installed,
* add option to stop on rate limiting.

Resources:

* [docs.scrapy.org](https://docs.scrapy.org/en/latest) - docs
* [playwright.dev](https://playwright.dev/python/docs/intro) - docs
* [scrapy/scrapy](https://github.com/scrapy/scrapy) - GitHub
* [scrapy-plugins/scrapy-playwright](https://github.com/scrapy-plugins/scrapy-playwright) - GitHub

Tested on Kali Linux v2024.2 (64-bit).

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

python3 -m pip install dist/scrapy-scraper-4.0-py3-none-any.whl
```

## How to Run

Example, start in-scope crawling from `https://example.com/home`, download in-scope JavaScript files, and extract links:

```fundamental
scrapy-scraper -u https://example.com/home -o results.json -a random -s 2 -rs -d downloads
```

Example, start in-scope crawling from URLs specified in `urls.txt`, take a screenshot of only the start URLs, and extract links:

```fundamental
scrapy-scraper -u urls.txt -o results.json -a random -s 2 -rs -p -ss screenshots
```

## Usage

```fundamental
Scrapy Scraper v4.0 ( github.com/ivan-sincek/scrapy-scraper )

Usage:   scrapy-scraper -u urls                     -o out          [-d downloads] [-ss screenshots]
Example: scrapy-scraper -u https://example.com/home -o results.json [-d downloads] [-ss screenshots]

DESCRIPTION
    Probe, crawl, scrape, and screenshot websites
URLS
    File containing URLs or a single URL to start collecting from
    -u, --urls = urls.txt | https://example.com/home | etc.
WHITELIST
    File containing whitelisted domain names to limit the scope
    Specify 'off' to disable domain whitelisting
    Default: limit the scope to domain names extracted from the starting URLs
    -w, --whitelist = whitelist.txt | off | etc.
PLAYWRIGHT
    Use Playwright's headless browser
    -p, --playwright
PLAYWRIGHT WAIT
    Wait time in seconds before fetching the page content
    -pw, --playwright-wait = 0.5 | 2 | 4 | etc.
CONCURRENT REQUESTS
    Number of concurrent requests
    Default: 30
    -cr, --concurrent-requests = 30 | 45 | etc.
CONCURRENT REQUESTS PER DOMAIN
    Number of concurrent requests per domain
    Default: 10
    -crd, --concurrent-requests-domain = 10 | 15 | etc.
SLEEP
    Sleep time in seconds between two consecutive requests to the same domain
    -s, --sleep = 1.5 | 3 | etc.
RANDOM SLEEP
    Randomize the sleep time between requests to vary between '0.5 * sleep' and '1.5 * sleep'
    -rs, --random-sleep
AUTO THROTTLE
    Automatically throttle concurrent requests based on load and latency
    Sleep time is still respected
    -at, --auto-throttle = 0.5 | 10 | 15 | 30 | etc.
RETRIES
    Number of retries per URL
    Default: 2
    -rt, --retries = 0 | 4 | etc.
RECURSION
    Recursion depth limit
    Specify 'off' to disable crawling
    Specify '0' for no limit
    Default: 1
    -r, --recursion = off | 0 | 5 | etc.
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
    Default: Scrapy Scraper/4.0
    -a, --user-agent = random[-all] | curl/3.30.1 | etc.
PROXY
    Web proxy to use
    -x, --proxy = http://127.0.0.1:8080 | etc.
DOWNLOADS
    Output directory for downloaded JavaScript files
    Automatically beautifies the files
    -d, --downloads = downloads | etc.
SCREENSHOTS
    Output directory for screenshots
    -ss, --screenshots = screenshots | etc.
OUT
    Output file
    -o, --out = results.json | etc.
DEBUG
    Enable debug output
    -dbg, --debug
```

## Images

<p align="center"><img src="https://raw.githubusercontent.com/ivan-sincek/scrapy-scraper/refs/heads/main/img/scraping.png" alt="Scraping"></p>

<p align="center">Figure 1 - Scraping</p>
