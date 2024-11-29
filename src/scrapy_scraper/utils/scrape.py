#!/usr/bin/env python3

from . import array, file, general, stopwatch

from bs4 import BeautifulSoup

import asyncio, jsbeautifier, os, random, scrapy, scrapy.crawler, scrapy.utils.project, typing, urllib.parse

class ScrapyScraperSpider(scrapy.Spider):

	def __init__(
		self,
		urls           : list[str],
		whitelist      : list[str],
		links          : bool,
		playwright     : bool,
		playwright_wait: float,
		headers        : dict[str, str],
		cookies        : dict[str, str],
		user_agents    : list[str],
		proxy          : str,
		directory      : str,
		out            : str,
		debug          : bool
	):
		"""
		Class for managing Scrapy's spider.
		"""
		self.name              = "ScrapyScraperSpider"
		self.start_urls        = urls
		self.allowed_domains   = whitelist
		self.__links           = links
		self.__playwright      = playwright
		self.__playwright_wait = playwright_wait
		self.__headers         = headers
		self.__cookies         = cookies
		self.__user_agents     = user_agents
		self.__user_agents_len = len(self.__user_agents)
		self.__proxy           = proxy
		self.__directory       = directory
		self.__out             = out
		self.__debug           = debug
		self.__context         = 0
		self.__crawled         = []
		self.__collected       = []

	def __print_start_urls(self):
		"""
		Print start URLS.
		"""
		general.print_green("Start URLs:")
		for url in self.start_urls:
			print(url)

	def __print_allowed_domains(self):
		"""
		Print allowed domains/subdomains.
		"""
		if self.allowed_domains:
			general.print_cyan("Allowed domains/subdomains:")
			for domain in self.allowed_domains:
				print(f"*.{domain}")
		else:
			general.print_red("Domain whitelisting is off!")

	def start_requests(self):
		"""
		Main method.
		"""
		self.__print_start_urls()
		self.__print_allowed_domains()
		print(general.get_timestamp("Crawling and scraping..."))
		print("Press CTRL + C to exit early - results will be saved, be patient")
		for url in self.start_urls:
			yield scrapy.Request(
				url         = url,
				headers     = self.__get_headers(),
				cookies     = self.__cookies,
				meta        = self.__get_metadata(),
				errback     = self.__error,
				callback    = self.__success,
				dont_filter = False
			)

	def __get_headers(self) -> dict[str, str]:
		"""
		Get default HTTP request headers.
		"""
		default_headers = {
			"User-Agent"               : self.__get_user_agent(),
			"Accept-Language"          : "en-US, *",
			"Accept"                   : "*/*",
			"Referer"                  : "https://www.google.com/",
			"Upgrade-Insecure-Requests": "1"
		}
		headers = {}
		for name, value in default_headers.items():
			if value:
				headers[name.lower()] = value
		for name, value in self.__headers.items(): # override
			headers[name.lower()] = value
		return headers

	def __get_user_agent(self):
		"""
		Get a [random] user agent.\n
		Returns an empty string if there are no user agents.
		"""
		user_agent = ""
		if self.__user_agents_len > 0:
			user_agent = self.__user_agents[random.randint(0, self.__user_agents_len - 1)]
		return user_agent

	def __get_metadata(self) -> dict[str, typing.Any]:
		"""
		Get Scrapy's request metadata.
		"""
		self.__context += 1
		tmp                                = {}
		tmp["playwright"                 ] = self.__playwright
		tmp["playwright_context"         ] = str(self.__context)
		tmp["playwright_include_page"    ] = self.__playwright
		tmp["playwright_context_kwargs"  ] = {}
		tmp["playwright_context_kwargs"  ]["ignore_https_errors"] = True
		tmp["playwright_context_kwargs"  ]["java_script_enabled"] = True
		tmp["playwright_context_kwargs"  ]["accept_downloads"   ] = False
		tmp["playwright_context_kwargs"  ]["bypass_csp"         ] = False
		tmp["playwright_page_goto_kwargs"] = {"wait_until": "load"}
		tmp["proxy"                      ] = self.__proxy
		tmp["cookiejar"                  ] = 1
		tmp["dont_merge_cookies"         ] = False
		return tmp

	# ------------------------------------

	def closed(self, reason: typing.Any):
		"""
		On close callback.
		"""
		self.__crawled = array.unique(self.__crawled)
		print(f"Total unique URLs crawled: {len(self.__crawled)}")
		self.__collected = array.unique(self.__collected + self.__crawled)
		print(f"Total unique URLs collected: {len(self.__collected)}")
		stopwatch.stopwatch.stop()
		if self.__collected:
			file.write_array(sorted(self.__collected, key = str.casefold), self.__out)

	# ------------------------------------

	async def __error(self, failure: typing.Any):
		"""
		Error callback.
		"""
		status = failure.value.response.status if failure.check(scrapy.spidermiddlewares.httperror.HttpError) else 0
		url    = failure.request.url
		error  = str(failure.value).splitlines()[0]
		if self.__playwright:
			page = failure.request.meta["playwright_page"]
			await page.close()
			await page.context.close()
		self.__print_error(status, url, error)

	def __print_error(self, status: int, url: str, message: str):
		"""
		Print error.
		"""
		if self.__debug:
			if status:
				url = f"{status} {url}"
			general.print_red(f"[ ERROR ] {url} -> {message}")

	# ------------------------------------

	async def __success(self, response: typing.Any):
		"""
		Success callback.
		"""
		status  = response.status
		url     = response.url
		content = ""
		if self.__playwright:
			page = response.request.meta["playwright_page"]
			if self.__playwright_wait > 0:
				await asyncio.sleep(self.__playwright_wait)
			content = await page.content()
			await page.close()
			await page.context.close()
		else:
			content = response.body
		# --------------------------------
		self.__crawled.append(url)
		self.__print_success(status, url)
		# --------------------------------
		if self.__directory:
			self.__download_js(url, content)
		# --------------------------------
		links = self.__extract_links(url, scrapy.http.HtmlResponse(url = url, body = content, encoding = "UTF-8") if self.__playwright else response)
		self.__collected.extend(links)
		for link in links:
			yield response.follow(
				url         = link,
				headers     = self.__get_headers(),
				cookies     = self.__cookies,
				meta        = self.__get_metadata(),
				errback     = self.__error,
				callback    = self.__success,
				dont_filter = False
			)

	def __print_success(self, status: int, url: str):
		"""
		Print success.
		"""
		if self.__debug:
			general.print_green(f"[ OK ] {status} {url}")

	def __download_js(self, url: str, content: str | bytes):
		"""
		Download JavaScript files.
		"""
		filename = urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1]
		if filename.lower().endswith(".js"):
			filename = os.path.join(self.__directory, filename)
			if not os.path.exists(filename):
				try:
					soup = BeautifulSoup(content, "html.parser")
					open(filename, "w").write(jsbeautifier.beautify(soup.get_text()))
				except Exception as ex:
					self.__print_exception(url, str(ex))

	def __extract_links(self, url: str, response: typing.Any):
		"""
		Extract links.\n
		Returns a unique list.
		"""
		tmp = []
		try:
			tmp.extend(self.__extract_links_xpath(url, response, "script", "src" ))
			tmp.extend(self.__extract_links_xpath(url, response, "a"     , "href"))
			tmp.extend(self.__extract_links_xpath(url, response, "link"  , "href"))
		except (UnicodeEncodeError, AttributeError) as ex:
			self.__print_exception(url, str(ex))
		return array.unique(tmp)

	def __extract_links_xpath(self, url: str, response: typing.Any, tag: str, attr: str):
		"""
		Extract links based on the specified XPath.
		"""
		tmp = []
		for link in response.xpath(f"//{tag}[@{attr}]"):
			link   = link.xpath(f"@{attr}").get()
			obj    = urllib.parse.urlsplit(link)
			scheme = obj.scheme
			domain = obj.netloc.lower()
			if scheme and scheme not in ["http", "https"]:
				continue
			elif not self.__links and domain and not self.__is_allowed(domain):
				continue
			tmp.append(urllib.parse.urljoin(url, link))
		return tmp

	def __is_allowed(self, domain: str):
		"""
		Check if a domain name is in the scope.
		"""
		return not self.allowed_domains or any(domain == allowed or domain.endswith(f".{allowed}") for allowed in self.allowed_domains)

	def __print_exception(self, url: str, message: str):
		"""
		Print exception.
		"""
		if self.__debug:
			general.print_red(f"[ EXCEPTION ] {url} -> {message}")

# ----------------------------------------

class ScrapyScraper:

	def __init__(
		self,
		urls                      : list[str],
		whitelist                 : list[str],
		links                     : bool,
		playwright                : bool,
		playwright_wait           : float,
		concurrent_requests       : int,
		concurrent_requests_domain: int,
		sleep                     : float,
		random_sleep              : bool,
		auto_throttle             : float,
		retries                   : int,
		recursion                 : int,
		request_timeout           : float,
		headers                   : dict[str, str],
		cookies                   : dict[str, str],
		user_agents               : list[str],
		proxy                     : str,
		directory                 : str,
		out                       : str,
		debug                     : bool
	):
		"""
		Class for managing Scrapy's runner.
		"""
		self.__urls                       = urls
		self.__whitelist                  = whitelist
		self.__links                      = links
		self.__playwright                 = playwright
		self.__playwright_wait            = playwright_wait
		self.__concurrent_requests        = concurrent_requests
		self.__concurrent_requests_domain = concurrent_requests_domain
		self.__sleep                      = sleep
		self.__random_sleep               = random_sleep
		self.__auto_throttle              = auto_throttle
		self.__retries                    = retries
		self.__recursion                  = recursion
		self.__request_timeout            = request_timeout # all timeouts
		self.__headers                    = headers
		self.__cookies                    = cookies
		self.__user_agents                = user_agents
		self.__proxy                      = proxy
		self.__directory                  = directory
		self.__out                        = out
		self.__debug                      = debug
		self.__headless_browser           = True
		self.__browser_type               = "chromium" # Playwright's headless browser
		self.__handle_sigint              = False
		self.__max_redirects              = 10

	def __page_block(self, request: typing.Any):
		"""
		Types of content to block while using Playwright's headless browser.
		"""
		return request.resource_type in ["fetch", "stylesheet", "image", "ping", "font", "media", "imageset", "beacon", "csp_report", "object", "texttrack", "manifest"]

	def run(self):
		"""
		Configure the settings and run the Chad Extractor spider.
		"""
		settings = scrapy.utils.project.get_project_settings()
		# --------------------------------
		settings["COOKIES_ENABLED"         ] = True
		settings["DOWNLOAD_TIMEOUT"        ] = self.__request_timeout # connect / read timeout
		settings["DOWNLOAD_DELAY"          ] = self.__sleep
		settings["RANDOMIZE_DOWNLOAD_DELAY"] = self.__random_sleep
		settings["HTTPPROXY_ENABLED"       ] = bool(self.__proxy)
		# --------------------------------
		settings["EXTENSIONS"]["scrapy.extensions.throttle.AutoThrottle"] = 100
		# --------------------------------
		settings["AUTOTHROTTLE_ENABLED"           ] = self.__auto_throttle > 0
		settings["AUTOTHROTTLE_DEBUG"             ] = False
		settings["AUTOTHROTTLE_START_DELAY"       ] = self.__sleep
		settings["AUTOTHROTTLE_MAX_DELAY"         ] = settings["AUTOTHROTTLE_START_DELAY"] + 30
		settings["AUTOTHROTTLE_TARGET_CONCURRENCY"] = self.__auto_throttle
		# --------------------------------
		settings["CONCURRENT_REQUESTS"           ] = self.__concurrent_requests
		settings["CONCURRENT_REQUESTS_PER_DOMAIN"] = self.__concurrent_requests_domain
		settings["RETRY_ENABLED"                 ] = self.__retries > 0
		settings["RETRY_TIMES"                   ] = self.__retries
		settings["REDIRECT_ENABLED"              ] = self.__max_redirects > 0
		settings["REDIRECT_MAX_TIMES"            ] = self.__max_redirects
		settings["DEPTH_LIMIT"                   ] = self.__recursion
		# --------------------------------
		settings["ROBOTSTXT_OBEY"                      ] = False
		settings["TELNETCONSOLE_ENABLED"               ] = False
		settings["LOG_ENABLED"                         ] = False
		settings["REQUEST_FINGERPRINTER_IMPLEMENTATION"] = "2.7"
		# --------------------------------
		if self.__playwright:
			settings["DOWNLOAD_HANDLERS"]["https"] = "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
			settings["DOWNLOAD_HANDLERS"]["http" ] = "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
			settings["TWISTED_REACTOR"           ] = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
			settings["PLAYWRIGHT_LAUNCH_OPTIONS" ] = {
				"headless"     : self.__headless_browser,
				"handle_sigint": self.__handle_sigint,
				"proxy"        : {"server": self.__proxy} if self.__proxy else None
			}
			settings["PLAYWRIGHT_BROWSER_TYPE"              ] = self.__browser_type
			settings["PLAYWRIGHT_ABORT_REQUEST"             ] = self.__page_block
			settings["PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT"] = self.__request_timeout * 1000
		# --------------------------------
		scrapy_scraper_spider = scrapy.crawler.CrawlerProcess(settings)
		scrapy_scraper_spider.crawl(ScrapyScraperSpider, self.__urls, self.__whitelist, self.__links, self.__playwright, self.__playwright_wait, self.__headers, self.__cookies, self.__user_agents, self.__proxy, self.__directory, self.__out, self.__debug)
		scrapy_scraper_spider.start()
		scrapy_scraper_spider.join()
