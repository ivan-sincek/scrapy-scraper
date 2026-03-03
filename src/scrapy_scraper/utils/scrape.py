#!/usr/bin/env python3

from . import array, file, general, stopwatch

from bs4 import BeautifulSoup

from twisted.python.failure             import Failure
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.http                        import Request, HtmlResponse
from playwright.async_api               import Request as PlaywrightRequest, Page as PlaywrightPage, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

import asyncio, dataclasses, jsbeautifier, os, random, scrapy, scrapy.crawler, scrapy.utils.project, typing, urllib.parse

@dataclasses.dataclass
class Crawled:
	url         : str  = ""
	status      : int  = -1
	is_start_url: bool = False

@dataclasses.dataclass
class Links:
	in_scope    : list[str] = dataclasses.field(default_factory = list)
	out_of_scope: list[str] = dataclasses.field(default_factory = list)

@dataclasses.dataclass
class Collection:
	crawled: list[Crawled] = dataclasses.field(default_factory = list[Crawled])
	links  : Links         = dataclasses.field(default_factory = Links)

class ScrapyScraperSpider(scrapy.Spider):

	def __init__(
		self,
		urls           : list[str],
		whitelist      : list[str],
		playwright     : bool,
		playwright_wait: float,
		recursion      : int,
		headers        : dict[str, str],
		cookies        : dict[str, str],
		user_agents    : list[str],
		proxy          : str,
		downloads      : str,
		screenshots    : str,
		out            : str,
		debug          : bool
	):
		"""
		Class for managing Scrapy's spider.
		"""
		self.name              = "ScrapyScraperSpider"
		self.start_urls        = urls
		self.allowed_domains   = whitelist
		self.__playwright      = playwright
		self.__playwright_wait = playwright_wait
		self.__crawl           = recursion > -1
		self.__headers         = headers
		self.__cookies         = cookies
		self.__user_agents     = user_agents
		self.__user_agents_len = len(self.__user_agents)
		self.__proxy           = proxy
		self.__downloads       = downloads
		self.__screenshots     = screenshots
		self.__out             = out
		self.__debug           = debug
		self.__context         = 0
		self.__collection      = Collection()

	def __print_start_urls(self):
		"""
		Print start URLS.
		"""
		general.print_green("Start URLs:")
		for url in self.start_urls:
			print(url)

	def __print_allowed_domains(self):
		"""
		Print allowed [sub]domains.
		"""
		if self.allowed_domains:
			general.print_cyan("Allowed [sub]domains:")
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
		print(general.get_timestamp("Collecting..."))
		print("Press CTRL + C to exit early - results will be saved, please be patient")
		for url in self.start_urls:
			yield scrapy.Request(
				url         = url,
				headers     = self.__get_headers(),
				cookies     = self.__cookies,
				meta        = self.__get_metadata(True, True),
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

	def __get_metadata(self, is_start_url = False, take_screenshot = False) -> dict[str, typing.Any]:
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
		tmp["is_start_url"               ] = is_start_url
		tmp["take_screenshot"            ] = take_screenshot
		return tmp

	# ------------------------------------

	def closed(self, reason: str):
		"""
		On close callback.
		"""
		self.__collection.crawled.sort(key = lambda x: x.url.casefold(), reverse = True)
		self.__collection.links.in_scope = sorted(array.unique(self.__collection.links.in_scope), key = str.casefold, reverse = True)
		self.__collection.links.out_of_scope = sorted(array.unique(self.__collection.links.out_of_scope), key = str.casefold, reverse = True)
		print(f"Total unique URLs crawled: {len(self.__collection.crawled)}")
		print(f"Total unique in-scope links extracted: {len(self.__collection.links.in_scope)}")
		print(f"Total unique out-of-scope links extracted: {len(self.__collection.links.out_of_scope)}")
		stopwatch.stopwatch.stop()
		if len(self.__collection.crawled) > 0:
			file.overwrite(general.jdump(dataclasses.asdict(self.__collection)), self.__out)

	# ------------------------------------

	async def __error(self, failure: Failure):
		"""
		Error callback.
		"""
		request : Request      = failure.request
		response: HtmlResponse = failure.value.response
		status = response.status if failure.check(HttpError) else -1
		url    = request.url
		error  = str(failure.value).splitlines()[0]
		if self.__playwright:
			page: PlaywrightPage = request.meta["playwright_page"]
			await page.close()
			await page.context.close()
		self.__print_error(status, url, error)

	def __print_error(self, status: int, url: str, message: str):
		"""
		Print error.
		"""
		if self.__debug:
			if status > -1:
				url = f"{status} {url}"
			general.print_red(f"[ ERROR ] {url} -> {message}")

	# ------------------------------------

	async def __success(self, response: HtmlResponse):
		"""
		Success callback.
		"""
		status  = response.status
		url     = response.url
		content = ""
		if self.__playwright:
			page: PlaywrightPage = response.request.meta["playwright_page"]
			if self.__playwright_wait > 0:
				await asyncio.sleep(self.__playwright_wait)
			content = await page.content()
			if self.__screenshots and response.meta.get("take_screenshot", False):
				await self.__screenshot(url, page)
			await page.close()
			await page.context.close()
		else:
			content = response.body
		if self.__downloads:
			self.__download(url, content)
		in_scope_links, out_of_scope_links = self.__extract_links(url, HtmlResponse(url = url, body = content, encoding = "UTF-8") if self.__playwright else response)
		self.__collection.crawled.append(Crawled(url, status, response.meta.get("is_start_url", False)))
		self.__collection.links.in_scope.extend(in_scope_links)
		self.__collection.links.out_of_scope.extend(out_of_scope_links)
		self.__print_success(status, url)
		# --------------------------------
		if self.__crawl:
			for link in in_scope_links:
				yield response.follow(
					url         = link,
					headers     = self.__get_headers(),
					cookies     = self.__cookies,
					meta        = self.__get_metadata(False, False),
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

	# ------------------------------------

	async def __screenshot(self, url: str, page: PlaywrightPage):
		"""
		Take a screenshot.
		"""
		filename = os.path.join(self.__screenshots, self.__get_url_filename(url)) + ".png"
		if not os.path.exists(filename):
			try:
				await page.screenshot(path = filename, full_page = False)
			except (PlaywrightError, PlaywrightTimeoutError) as ex:
				self.__print_exception(url, str(ex))

	def __download(self, url: str, content: str | bytes):
		"""
		Download a JavaScript file.
		"""
		if url.lower().endswith(".js"):
			filename = os.path.join(self.__downloads, self.__get_url_filename(url))
			if not os.path.exists(filename):
				try:
					soup = BeautifulSoup(content, "html.parser")
					open(filename, "w").write(jsbeautifier.beautify(soup.get_text()))
				except Exception as ex:
					self.__print_exception(url, str(ex))

	def __get_url_filename(self, url: str):
		"""
		Derive a filename from a URL.
		"""
		obj      = urllib.parse.urlsplit(url)
		scheme   = obj.scheme.lower()
		domain   = obj.netloc.lower()
		port     = str(obj.port) if obj.port else ""
		path     = obj.path.strip("/").replace("/", ".")
		filename = ""
		for part in [scheme, domain, port, path]:
			if part:
				filename = f"{filename}_{part}"
		return filename

	# ------------------------------------

	def __extract_links(self, url: str, response: HtmlResponse):
		"""
		Extract links.\n
		Returns a unique list.
		"""
		in_scope = []
		out_of_scope = []
		for tag, attr in (("script", "src"),("a", "href"),("link", "href")):
			try:
				tmp1, tmp2 = self.__extract_links_xpath(url, response, tag, attr)
				in_scope.extend(tmp1)
				out_of_scope.extend(tmp2)
			except (UnicodeEncodeError, AttributeError) as ex:
				self.__print_exception(url, str(ex))
		return array.unique(in_scope), array.unique(out_of_scope)

	def __extract_links_xpath(self, url: str, response: HtmlResponse, tag: str, attr: str):
		"""
		Extract links based on the specified XPath.
		"""
		in_scope = []
		out_of_scope = []
		for link in response.xpath(f"//{tag}[@{attr}]"):
			link = link.xpath(f"@{attr}").get()
			if not link:
				continue
			obj = urllib.parse.urlsplit(link)
			if obj.scheme and obj.scheme.lower() not in ["http", "https"]:
				continue
			if not obj.scheme and not obj.netloc:
				in_scope.append(urllib.parse.urljoin(url, link))
				continue
			if obj.scheme and obj.netloc:
				if self.__is_in_scope(obj.netloc):
					in_scope.append(link)
				else:
					out_of_scope.append(link)
		return array.unique(in_scope), array.unique(out_of_scope)

	def __is_in_scope(self, domain: str):
		"""
		Check if a domain name is in the scope.
		"""
		domain = domain.lower()
		return not self.allowed_domains or any(domain == allowed or domain.endswith(f".{allowed}") for allowed in self.allowed_domains)

	# ------------------------------------

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
		downloads                 : str,
		screenshots               : str,
		out                       : str,
		debug                     : bool
	):
		"""
		Class for managing Scrapy's runner.
		"""
		self.__urls                       = urls
		self.__whitelist                  = whitelist
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
		self.__downloads                  = downloads
		self.__screenshots                = screenshots
		self.__out                        = out
		self.__debug                      = debug
		self.__headless_browser           = True
		self.__browser_type               = "chromium" # Playwright's headless browser
		self.__handle_sigint              = False
		self.__max_redirects              = 10

	def __page_block(self, request: PlaywrightRequest):
		"""
		Types of content to block while using Playwright's headless browser.\n
		Skipped if taking screenshots.
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
		settings["AUTOTHROTTLE_MAX_DELAY"         ] = self.__sleep + 30
		settings["AUTOTHROTTLE_TARGET_CONCURRENCY"] = self.__auto_throttle
		# --------------------------------
		settings["CONCURRENT_REQUESTS"           ] = self.__concurrent_requests
		settings["CONCURRENT_REQUESTS_PER_DOMAIN"] = self.__concurrent_requests_domain
		settings["RETRY_ENABLED"                 ] = self.__retries > 0
		settings["RETRY_TIMES"                   ] = self.__retries
		settings["REDIRECT_ENABLED"              ] = self.__max_redirects > 0
		settings["REDIRECT_MAX_TIMES"            ] = self.__max_redirects
		settings["DEPTH_LIMIT"                   ] = self.__recursion if self.__recursion > -1 else 1
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
			settings["PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT"] = self.__request_timeout * 1000
			settings["PLAYWRIGHT_ABORT_REQUEST"             ] = None if self.__screenshots else self.__page_block
		# --------------------------------
		scrapy_scraper_spider = scrapy.crawler.CrawlerProcess(settings)
		scrapy_scraper_spider.crawl(ScrapyScraperSpider, self.__urls, self.__whitelist, self.__playwright, self.__playwright_wait, self.__recursion, self.__headers, self.__cookies, self.__user_agents, self.__proxy, self.__downloads, self.__screenshots, self.__out, self.__debug)
		scrapy_scraper_spider.start()
		scrapy_scraper_spider.join()
