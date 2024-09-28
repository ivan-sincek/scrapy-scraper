#!/usr/bin/env python3

import argparse, asyncio, colorama, datetime, jsbeautifier, os, random, re, scrapy, scrapy.crawler, scrapy.utils.project, sys, termcolor, tldextract, urllib.parse

from bs4 import BeautifulSoup

colorama.init(autoreset = True)

# ----------------------------------------

class Stopwatch:

	def __init__(self):
		self.__start = datetime.datetime.now()

	def stop(self):
		self.__end = datetime.datetime.now()
		print(f"Script has finished in {self.__end - self.__start}")

stopwatch = Stopwatch()

# ----------------------------------------

def parse_float(value):
    tmp = None
    try:
        tmp = float(value)
    except ValueError:
        pass
    return tmp

def validate_domains(values):
    if not isinstance(values, list):
        values = [values]
    tmp = []
    const = "."
    for value in values:
        obj = tldextract.extract(value)
        if obj.domain and obj.suffix:
            domain = obj.domain + const + obj.suffix
            if obj.subdomain:
                domain = obj.subdomain + const + domain
            tmp.append(domain.lower())
    return unique(tmp)

def unique(sequence):
	seen = set()
	return [x for x in sequence if not (x in seen or seen.add(x))]

DEFAULT_ENCODING = "ISO-8859-1"

def read_file(file):
	tmp = []
	with open(file, "r", encoding = DEFAULT_ENCODING) as stream:
		for line in stream:
			line = line.strip()
			if line:
				tmp.append(line)
	return unique(tmp)

def write_array(data, out):
	confirm = "yes"
	if os.path.isfile(out):
		print(f"'{out}' already exists")
		confirm = input("Overwrite the output file (yes): ")
	if confirm.lower() == "yes":
		try:
			with open(out, "w") as stream:
				for line in data:
					stream.write(str(line).strip() + "\n")
			print(f"Results have been saved to '{out}'")
		except FileNotFoundError:
			print(f"Cannot save results to '{out}'")

def get_header_key_value(header):
	key = ""; value = ""
	if re.search(r"^[^\:]+\:.+$", header):
		key, value = header.split(":", 1)
	return key.strip(), value.strip()

def get_cookie_key_value(cookie):
	key = ""; value = ""
	if re.search(r"^[^\=\;]+\=[^\=\;]+$|^[^\=\;]+\=$", cookie):
		key, value = cookie.split("=", 1)
	return key.strip(), value.strip()

DEFAULT_USER_AGENT = "Scrapy Scraper/2.4"

def get_all_user_agents():
	array = []
	file = os.path.join(os.path.abspath(os.path.split(__file__)[0]), "user_agents.txt")
	if os.path.isfile(file) and os.access(file, os.R_OK) and os.stat(file).st_size > 0:
		with open(file, "r", encoding = DEFAULT_ENCODING) as stream:
			for line in stream:
				line = line.strip()
				if line:
					array.append(line)
	return array if array else [DEFAULT_USER_AGENT]

def get_random_user_agent():
	array = get_all_user_agents()
	return array[random.randint(0, len(array) - 1)]

# ----------------------------------------

class ScrapyScraperSpider(scrapy.Spider):

	def __init__(self, urls, whitelist, links, playwright, playwright_wait, headers, cookies, user_agents, proxy, directory, out, debug):
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
		self.__dont_filter     = False # if "True", allow duplicate requests
		self.__context         = 0
		self.__crawled         = []
		self.__collected       = []

	def start_requests(self):
		self.__print_start_urls()
		self.__print_allowed_domains()
		print("Crawling and scraping...")
		print("Press CTRL + C to exit early - results will be saved but please be patient")
		for url in self.start_urls:
			yield scrapy.Request(
				url         = url,
				headers     = self.__get_headers(),
				cookies     = self.__cookies,
				meta        = self.__get_meta(),
				errback     = self.__exception,
				callback    = self.__parse,
				dont_filter = self.__dont_filter
			)

	def closed(self, reason):
		self.__crawled = unique(self.__crawled)
		print(f"Total unique URLs crawled: {len(self.__crawled)}")
		self.__collected = unique(self.__collected)
		print(f"Total unique URLs collected: {len(self.__collected)}")
		stopwatch.stop()
		if self.__collected:
			write_array(sorted(self.__collected, key = str.casefold), self.__out)

	def __print_start_urls(self):
		termcolor.cprint("Normalized start URLs:", "green")
		for url in self.start_urls:
			print(url)

	def __print_allowed_domains(self):
		if self.allowed_domains:
			termcolor.cprint("Allowed domains/subdomains:", "cyan")
			for domain in self.allowed_domains:
				print("*." + domain)
		else:
			termcolor.cprint("Domain whitelisting is off!", "red")

	def __get_headers(self):
		default = {
			"User-Agent"               : self.__get_user_agent(),
			"Accept-Language"          : "en-US, *",
			"Accept"                   : "*/*",
			"Connection"               : "keep-alive",
			"Referer"                  : "https://www.google.com/",
			"Upgrade-Insecure-Requests": "1"
		}
		tmp = {}
		for key, value in default.items():
			tmp[key.lower()] = value
		for key, value in self.__headers.items(): # override
			tmp[key.lower()] = value
		return tmp

	def __get_user_agent(self):
		return self.__user_agents[random.randint(0, self.__user_agents_len - 1)]

	def __get_meta(self):
		self.__context += 1
		return {
			"playwright"                 : self.__playwright,
			"playwright_context"         : str(self.__context),
			"playwright_context_kwargs"  : {
				"ignore_https_errors"    : True,
				"java_script_enabled"    : True,
				"accept_downloads"       : False,
				"bypass_csp"             : False
			},
			"playwright_include_page"    : self.__playwright,
			"playwright_page_goto_kwargs": {"wait_until": "load"},
			"proxy"                      : self.__proxy,
			"cookiejar"                  : 1,
			"dont_merge_cookies"         : False
		}

	async def __exception(self, failure):
		status = 0
		error  = str(failure.value).splitlines()[0]
		if failure.check(scrapy.spidermiddlewares.httperror.HttpError):
			status = failure.value.response.status
		if self.__playwright:
			page = failure.request.meta["playwright_page"]
			await page.close()
			await page.context.close()
		self.__print_error(status, failure.request.url, error)

	def __print_error(self, status, url, error):
		if self.__debug:
			if status:
				url = f"{status} {url}"
			termcolor.cprint(f"[ ERROR ] {url} -> {error}", "red")

	# ------------------------------------

	async def __parse(self, response):
		status = response.status
		url    = response.url
		body   = ""
		if self.__playwright:
			page = response.request.meta["playwright_page"]
			if self.__playwright_wait > 0:
				await asyncio.sleep(self.__playwright_wait)
			body = await page.content() # text, from Playwright
			await page.close()
			await page.context.close()
		else:
			body = response.body # raw, from Scrapy
		self.__crawled.append(url)
		self.__collected.append(url)
		self.__print_success(status, url)
		# --------------------------------
		if self.__directory:
			self.__download_js(url, body)
		# --------------------------------
		links = self.__extract_links(url, scrapy.http.HtmlResponse(url = url, body = body, encoding = "UTF-8") if self.__playwright else response)
		if self.__links:
			self.__collected.extend(links)
			for link in links:
				yield response.follow(
					url         = link,
					headers     = self.__get_headers(),
					cookies     = self.__cookies,
					meta        = self.__get_meta(),
					errback     = self.__exception,
					callback    = self.__parse,
					dont_filter = self.__dont_filter
				)

	def __print_success(self, status, url):
		if self.__debug:
			termcolor.cprint(f"[ OK ] {status} {url}", "green")

	def __download_js(self, url, body):
		file = urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1]
		if file.lower().endswith(".js"):
			file = os.path.join(self.__directory, file)
			if not os.path.exists(file):
				try:
					soup = BeautifulSoup(body, "html.parser")
					open(file, "w").write(jsbeautifier.beautify(soup.get_text()))
				except Exception as ex:
					self.__print_ex(url, ex)

	def __extract_links(self, url, response):
		tmp = []
		try:
			for link in unique(scrapy.linkextractors.LinkExtractor(
				tags  = ["a", "link", "script"],
				attrs = ["href", "src"]
			).extract_links(response)):
				link = urllib.parse.urljoin(url, link.url)
				if urllib.parse.urlsplit(link).scheme.lower() in ["http", "https"]:
					tmp.append(link)
		except (UnicodeEncodeError, AttributeError) as ex:
			self.__print_ex(url, ex)
		return unique(tmp)

	def __print_ex(self, url, error):
		if self.__debug:
			termcolor.cprint(f"[ EXCEPTION ] {url} -> {error}", "red")

# ----------------------------------------
class ScrapyScraper:

	def __init__(self, urls, whitelist, links, playwright, playwright_wait, concurrent_requests, concurrent_requests_domain, sleep, random_sleep, auto_throttle, retries, recursion, request_timeout, headers, cookies, user_agents, proxy, directory, out, debug):
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
		self.__headers                    = headers
		self.__cookies                    = cookies
		self.__user_agents                = user_agents
		self.__proxy                      = proxy
		self.__directory                  = directory
		self.__out                        = out
		self.__debug                      = debug
		self.__request_timeout            = request_timeout # all timeouts
		self.__max_redirects              = 10
		self.__headless_browser           = True
		self.__handle_sigint              = False
		self.__browser_type               = "chromium" # Playwright's headless browser

	def run(self):
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

	def __page_block(self, request):
		return request.resource_type in ["fetch", "stylesheet", "image", "ping", "font", "media", "imageset", "beacon", "csp_report", "object", "texttrack", "manifest"]

# ----------------------------------------

class MyArgParser(argparse.ArgumentParser):

	def print_help(self):
		print("Scrapy Scraper v2.4 ( github.com/ivan-sincek/scrapy-scraper )")
		print("")
		print("Usage:   scrapy-scraper -u urls                     -o out         [-dir directory]")
		print("Example: scrapy-scraper -u https://example.com/home -o results.txt [-dir downloads]")
		print("")
		print("DESCRIPTION")
		print("    Crawl and scrape websites")
		print("URLS")
		print("    File with URLs or a single URL to start crawling and scraping from")
		print("    -u, --urls = urls.txt | https://example.com/home | etc.")
		print("WHITELIST")
		print("    File with whitelisted domains to limit the crawling scope")
		print("    Specify 'off' to disable domain whitelisting")
		print("    Default: domains extracted from the URLs")
		print("    -w, --whitelist = whitelist.txt | off | etc.")
		print("LINKS")
		print("    Include all links and sources (incl. 3rd party) in the output file")
		print("    -l, --links")
		print("PLAYWRIGHT")
		print("    Use Playwright's headless browser")
		print("    -p, --playwright")
		print("PLAYWRIGHT WAIT")
		print("    Wait time in seconds before fetching the content from the page")
		print("    Applies only if Playwright's headless browser is used")
		print("    -pw, --playwright-wait = 2 | 4 | etc.")
		print("CONCURRENT REQUESTS")
		print("    Number of concurrent requests")
		print("    Default: 30")
		print("    -cr, --concurrent-requests = 15 | 45 | etc.")
		print("CONCURRENT REQUESTS PER DOMAIN")
		print("    Number of concurrent requests per domain")
		print("    Default: 10")
		print("    -crd, --concurrent-requests-domain = 5 | 15 | etc.")
		print("SLEEP")
		print("    Sleep time in seconds between two consecutive requests to the same domain")
		print("    -s, --sleep = 1.5 | 3 | etc.")
		print("RANDOM SLEEP")
		print("    Randomize the sleep time on each request to vary between '0.5 * sleep' and '1.5 * sleep'")
		print("    -rs, --random-sleep")
		print("AUTO THROTTLE")
		print("    Auto throttle concurrent requests based on the load and latency")
		print("    Sleep time is still respected")
		print("    -at, --auto-throttle = 0.5 | 10 | 15 | 45 | etc.")
		print("RETRIES")
		print("    Number of retries per URL")
		print("    -rt, --retries = 2 | 4 | etc.")
		print("RECURSION")
		print("    Recursion depth limit")
		print("    Specify '0' for no limit")
		print("    Default: 1")
		print("    -r, --recursion = 0 | 2 | etc.")
		print("REQUEST TIMEOUT")
		print("    Request timeout in seconds")
		print("    Default: 60")
		print("    -t, --request-timeout = 30 | 90 | etc.")
		print("HEADER")
		print("    Specify any number of extra HTTP request headers")
		print("    -H, --header = \"Authorization: Bearer ey...\" | etc.")
		print("COOKIE")
		print("    Specify any number of extra HTTP cookies")
		print("    -b, --cookie = PHPSESSIONID=3301 | etc.")
		print("USER AGENT")
		print("    User agent to use")
		print(f"    Default: {DEFAULT_USER_AGENT}")
		print("    -a, --user-agent = curl/3.30.1 | random[-all] | etc.")
		print("PROXY")
		print("    Web proxy to use")
		print("    -x, --proxy = http://127.0.0.1:8080 | etc.")
		print("DIRECTORY")
		print("    Output directory")
		print("    All extracted JavaScript files will be saved in this directory")
		print("    -dir, --directory = downloads | etc.")
		print("OUT")
		print("    Output file")
		print("    -o, --out = results.txt | etc.")
		print("DEBUG")
		print("    Debug output")
		print("    -dbg, --debug")

	def error(self, message):
		if len(sys.argv) > 1:
			print("Missing a mandatory option (-u, -o) and/or optional (-w, -l, -p, -pw, -cr, -crd, -s, -rs, -at, -rt, -r, -t, -H, -b, -a, -x, -dir, -dbg)")
			print("Use -h or --help for more info")
		else:
			self.print_help()
		exit()

class Validate:

	def __init__(self):
		self.__proceed = True
		self.__parser  = MyArgParser()
		self.__parser.add_argument("-u"  , "--urls"                      , required = True , type   = str         , default = ""   )
		self.__parser.add_argument("-w"  , "--whitelist"                 , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-l"  , "--links"                     , required = False, action = "store_true", default = False)
		self.__parser.add_argument("-p"  , "--playwright"                , required = False, action = "store_true", default = False)
		self.__parser.add_argument("-pw" , "--playwright-wait"           , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-cr" , "--concurrent-requests"       , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-crd", "--concurrent-requests-domain", required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-s"  , "--sleep"                     , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-rs" , "--random-sleep"              , required = False, action = "store_true", default = False)
		self.__parser.add_argument("-at" , "--auto-throttle"             , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-rt" , "--retries"                   , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-r"  , "--recursion"                 , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-t"  , "--request-timeout"           , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-H"  , "--header"                    , required = False, action = "append"    , nargs   = "+"  )
		self.__parser.add_argument("-b"  , "--cookie"                    , required = False, action = "append"    , nargs   = "+"  )
		self.__parser.add_argument("-a"  , "--user-agent"                , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-x"  , "--proxy"                     , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-dir", "--directory"                 , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-o"  , "--out"                       , required = True , type   = str         , default = ""   )
		self.__parser.add_argument("-dbg", "--debug"                     , required = False, action = "store_true", default = False)

	def run(self):
		self.__args                            = self.__parser.parse_args()
		self.__args.urls                       = self.__parse_urls(self.__args.urls)                                             # required
		self.__args.whitelist                  = self.__parse_whitelist(self.__args.whitelist)                                   if self.__args.whitelist                  else (validate_domains(self.__args.urls) if self.__proceed else [])
		self.__args.playwright_wait            = self.__parse_playwright_wait(self.__args.playwright_wait)                       if self.__args.playwright_wait            else 0
		self.__args.concurrent_requests        = self.__parse_concurrent_requests(self.__args.concurrent_requests)               if self.__args.concurrent_requests        else 30
		self.__args.concurrent_requests_domain = self.__parse_concurrent_requests_domain(self.__args.concurrent_requests_domain) if self.__args.concurrent_requests_domain else 10
		self.__args.sleep                      = self.__parse_sleep(self.__args.sleep)                                           if self.__args.sleep                      else 0
		self.__args.auto_throttle              = self.__parse_auto_throttle(self.__args.auto_throttle)                           if self.__args.auto_throttle              else 0
		self.__args.retries                    = self.__parse_retries(self.__args.retries)                                       if self.__args.retries                    else 0
		self.__args.recursion                  = self.__parse_recursion(self.__args.recursion)                                   if self.__args.recursion                  else 1
		self.__args.request_timeout            = self.__parse_request_timeout(self.__args.request_timeout)                       if self.__args.request_timeout            else 60
		self.__args.header                     = self.__parse_header(self.__args.header)                                         if self.__args.header                     else {}
		self.__args.cookie                     = self.__parse_cookie(self.__args.cookie)                                         if self.__args.cookie                     else {}
		self.__args.user_agent                 = self.__parse_user_agent(self.__args.user_agent)                                 if self.__args.user_agent                 else [DEFAULT_USER_AGENT]
		self.__args.proxy                      = self.__parse_proxy(self.__args.proxy)                                           if self.__args.proxy                      else ""
		self.__args.directory                  = self.__parse_directory(self.__args.directory)                                   if self.__args.directory                  else ""
		self.__args                            = vars(self.__args)
		return self.__proceed

	def get_arg(self, key):
		return self.__args[key]

	def __error(self, msg):
		self.__proceed = False
		self.__print_error(msg)

	def __print_error(self, msg):
		print(f"ERROR: {msg}")

	def __validate_urls(self, values):
		if not isinstance(values, list):
			values = [values]
		tmp = []
		for value in values:
			data = {
				"schemes": ["http", "https"],
				"scheme_error": [
					f"URL scheme is required: {value}",
					f"Supported URL schemes are 'http' and 'https': {value}"
				],
				"domain_error": f"Invalid domain name: {value}",
				"port_error": f"Port number is out of range: {value}"
			}
			obj = urllib.parse.urlsplit(value)
			if not obj.scheme:
				self.__error(data["scheme_error"][0])
			elif obj.scheme not in data["schemes"]:
				self.__error(data["scheme_error"][1])
			elif not obj.netloc:
				self.__error(data["domain_error"])
			elif obj.port and (obj.port < 1 or obj.port > 65535):
				self.__error(data["port_error"])
			else:
				tmp.append(obj.geturl()) # normalize
		return unique(tmp)

	def __parse_urls(self, value):
		tmp = []
		if os.path.isfile(value):
			if not os.access(value, os.R_OK):
				self.__error("File with URLs does not have a read permission")
			elif not os.stat(value).st_size > 0:
				self.__error("File with URLs is empty")
			else:
				tmp = read_file(value)
				if not tmp:
					self.__error("No URLs were found")
				else:
					tmp = self.__validate_urls(tmp)
		else:
			tmp = self.__validate_urls(value)
		return tmp

	def __parse_whitelist(self, value):
		tmp = []
		if value.lower() == "off":
			pass
		elif not os.path.isfile(value):
			self.__error("File with whitelisted domains does not exist")
		elif not os.access(value, os.R_OK):
			self.__error("File with whitelisted domains does not have a read permission")
		elif not os.stat(value).st_size > 0:
			self.__error("File with whitelisted domains is empty")
		else:
			tmp = validate_domains(read_file(value))
			if not tmp:
				self.__error("No valid whitelisted domains were found")
		return tmp

	def __parse_playwright_wait(self, value):
		value = parse_float(value)
		if value is None:
			self.__error("Wait time must be numeric")
		elif value <= 0:
			self.__error("Wait time must be greater than zero")
		return value

	def __parse_concurrent_requests(self, value):
		if not value.isdigit():
			self.__error("Number of concurrent requests must be numeric")
		else:
			value = int(value)
			if value <= 0:
				self.__error("Number of concurrent requests must be greater than zero")
		return value

	def __parse_concurrent_requests_domain(self, value):
		if not value.isdigit():
			self.__error("Number of concurrent requests per domain must be numeric")
		else:
			value = int(value)
			if value <= 0:
				self.__error("Number of concurrent requests per domain must be greater than zero")
		return value

	def __parse_sleep(self, value):
		value = parse_float(value)
		if value is None:
			self.__error("Sleep time must be numeric")
		elif value <= 0:
			self.__error("Sleep time must be greater than zero")
		return value

	def __parse_auto_throttle(self, value):
		value = parse_float(value)
		if value is None:
			self.__error("Auto throttle must be numeric")
		elif value <= 0:
			self.__error("Auto throttle must be greater than zero")
		return value

	def __parse_retries(self, value):
		if not value.isdigit():
			self.__error("Number of retries must be numeric")
		else:
			value = int(value)
			if value <= 0:
				self.__error("Number of retries must be greater than zero")
		return value

	def __parse_recursion(self, value):
		if not value.isdigit():
			self.__error("Recursion depth limit must be numeric")
		else:
			value = int(value)
			if value < 0:
				self.__error("Recursion depth limit must be greater than or equal to zero")
		return value

	def __parse_request_timeout(self, value):
		value = parse_float(value)
		if value is None:
			self.__error("Request timeout must be numeric")
		elif value <= 0:
			self.__error("Request timeout must be greater than zero")
		return value

	def __parse_header(self, headers):
		tmp = {}
		for header in headers:
			header = header[0]
			key, value = get_header_key_value(header)
			if not key or not value:
				self.__error(f"Invalid header: {header}")
				continue
			tmp[key] = value
		return tmp

	def __parse_cookie(self, cookies):
		tmp = {}
		for cookie in cookies:
			cookie = cookie[0]
			key, value = get_cookie_key_value(cookie)
			if not key or not value:
				self.__error(f"Invalid cookie: {cookie}")
				continue
			tmp[key] = value
		return tmp

	def __parse_user_agent(self, value):
		lower = value.lower()
		if lower == "random-all":
			return get_all_user_agents()
		elif lower == "random":
			return [get_random_user_agent()]
		else:
			return [value]

	def __parse_proxy(self, value):
		tmp = urllib.parse.urlsplit(value)
		if not tmp.scheme:
			self.__error("Proxy URL: Scheme is required")
		elif tmp.scheme not in ["http", "https", "socks4", "socks4h", "socks5", "socks5h"]:
			self.__error("Proxy URL: Supported schemes are 'http[s]', 'socks4[h]', and 'socks5[h]'")
		elif not tmp.netloc:
			self.__error("Proxy URL: Invalid domain name")
		elif tmp.port and (tmp.port < 1 or tmp.port > 65535):
			self.__error("Proxy URL: Port number is out of range")
		return value

	def __parse_directory(self, value):
		if not os.path.isdir(value):
			self.__error("Output directory does not exist or is not a directory")
		return value

# ----------------------------------------

def main():
	validate = Validate()
	if validate.run():
		print("###########################################################################")
		print("#                                                                         #")
		print("#                           Scrapy Scraper v2.4                           #")
		print("#                                     by Ivan Sincek                      #")
		print("#                                                                         #")
		print("# Crawl and scrape websites.                                              #")
		print("# GitHub repository at github.com/ivan-sincek/scrapy-scraper.             #")
		print("# Feel free to donate ETH at 0xbc00e800f29524AD8b0968CEBEAD4cD5C5c1f105.  #")
		print("#                                                                         #")
		print("###########################################################################")
		scrapy_scraper = ScrapyScraper(
			validate.get_arg("urls"),
			validate.get_arg("whitelist"),
			validate.get_arg("links"),
			validate.get_arg("playwright"),
			validate.get_arg("playwright_wait"),
			validate.get_arg("concurrent_requests"),
			validate.get_arg("concurrent_requests_domain"),
			validate.get_arg("sleep"),
			validate.get_arg("random_sleep"),
			validate.get_arg("auto_throttle"),
			validate.get_arg("retries"),
			validate.get_arg("recursion"),
			validate.get_arg("request_timeout"),
			validate.get_arg("header"),
			validate.get_arg("cookie"),
			validate.get_arg("user_agent"),
			validate.get_arg("proxy"),
			validate.get_arg("directory"),
			validate.get_arg("out"),
			validate.get_arg("debug")
		)
		scrapy_scraper.run()

if __name__ == "__main__":
	main()
