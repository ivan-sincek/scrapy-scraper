#!/usr/bin/env python3

from . import config, cookie, directory, file, general, header, url

import argparse, bot_safe_agents, sys

class MyArgParser(argparse.ArgumentParser):

	def print_help(self):
		print(f"Scrapy Scraper {config.APP_VERSION} ( github.com/ivan-sincek/scrapy-scraper )")
		print("")
		print("Usage:   scrapy-scraper -u urls                     -o out         [-dir directory]")
		print("Example: scrapy-scraper -u https://example.com/home -o results.txt [-dir downloads]")
		print("")
		print("DESCRIPTION")
		print("    Crawl and scrape websites")
		print("URLS")
		print("    File containing URLs or a single URL to start crawling and scraping from")
		print("    -u, --urls = urls.txt | https://example.com/home | etc.")
		print("WHITELIST")
		print("    File containing whitelisted domain names to limit the scope")
		print("    Specify 'off' to disable domain whitelisting")
		print("    Default: limit the scope to domain names extracted from the URLs")
		print("    -w, --whitelist = whitelist.txt | off | etc.")
		print("LINKS")
		print("    Include all 3rd party links and sources in the output file")
		print("    -l, --links")
		print("PLAYWRIGHT")
		print("    Use Playwright's headless browser")
		print("    -p, --playwright")
		print("PLAYWRIGHT WAIT")
		print("    Wait time in seconds before fetching the page content")
		print("    -pw, --playwright-wait = 0.5 | 2 | 4 | etc.")
		print("CONCURRENT REQUESTS")
		print("    Number of concurrent requests")
		print("    Default: 30")
		print("    -cr, --concurrent-requests = 30 | 45 | etc.")
		print("CONCURRENT REQUESTS PER DOMAIN")
		print("    Number of concurrent requests per domain")
		print("    Default: 10")
		print("    -crd, --concurrent-requests-domain = 10 | 15 | etc.")
		print("SLEEP")
		print("    Sleep time in seconds between two consecutive requests to the same domain")
		print("    -s, --sleep = 1.5 | 3 | etc.")
		print("RANDOM SLEEP")
		print("    Randomize the sleep time between requests to vary between '0.5 * sleep' and '1.5 * sleep'")
		print("    -rs, --random-sleep")
		print("AUTO THROTTLE")
		print("    Auto throttle concurrent requests based on the load and latency")
		print("    Sleep time is still respected")
		print("    -at, --auto-throttle = 0.5 | 10 | 15 | 45 | etc.")
		print("RETRIES")
		print("    Number of retries per URL")
		print("    Default: 2")
		print("    -rt, --retries = 0 | 4 | etc.")
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
		print(f"    Default: {config.USER_AGENT}")
		print("    -a, --user-agent = random[-all] | curl/3.30.1 | etc.")
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
		print("    Enable debug output")
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
		"""
		Class for validating and managing CLI arguments.
		"""
		self.__parser = MyArgParser()
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

	def validate_args(self):
		"""
		Validate and return the CLI arguments.
		"""
		self.__success = True
		self.__args = self.__parser.parse_args()
		self.__validate_urls()
		self.__validate_whitelist()
		self.__validate_playwright_wait()
		self.__validate_concurrent_requests()
		self.__validate_concurrent_requests_domain()
		self.__validate_sleep()
		self.__validate_auto_throttle()
		self.__validate_retries()
		self.__validate_recursion()
		self.__validate_request_timeout()
		self.__validate_header()
		self.__validate_cookie()
		self.__validate_user_agent()
		self.__validate_proxy()
		self.__validate_directory()
		return self.__success, self.__args

	def __error(self, message: str):
		"""
		Set the success flag to 'False' to prevent the main task from executing, and print an error message.
		"""
		self.__success = False
		general.print_error(message)

	# ------------------------------------

	def __validate_urls(self):
		tmp = []
		if file.is_file(self.__args.urls):
			success, message = file.validate(self.__args.urls)
			if not success:
				self.__error(message)
			else:
				tmp = file.read_array(self.__args.urls)
				if not tmp:
					self.__error(f"No URLs were found in \"{self.__args.urls}\"")
				else:
					success, message = url.validate_multiple(tmp)
					if not success:
						self.__error(message)
		else:
			success, message = url.validate(self.__args.urls)
			if not success:
				self.__error(message)
			else:
				tmp = [self.__args.urls]
		self.__args.urls = tmp

	def __validate_whitelist(self):
		tmp = []
		if self.__args.whitelist.lower() == "off":
			pass
		elif self.__args.whitelist:
			if not file.is_file(self.__args.whitelist):
				self.__error(f"\"{self.__args.whitelist}\" does not exist")
			else:
				success, message = file.validate(self.__args.whitelist)
				if not success:
					self.__error(message)
				else:
					tmp = url.extract_fqdn_multiple(file.read_array(self.__args.whitelist))
					if not tmp:
						self.__error(f"No valid whitelisted domain names were found in \"{self.__args.whitelist}\"")
		elif self.__success:
			tmp = url.extract_fqdn_multiple(self.__args.urls)
			if not tmp:
				self.__error("No domain names could be extracted from the provided URLs for domain whitelisting")
		self.__args.whitelist = tmp

	def __validate_playwright_wait(self):
		tmp = 0
		if self.__args.playwright_wait:
			tmp = general.to_float(self.__args.playwright_wait)
			if tmp is None:
				self.__error("Playwright's wait time must be numeric")
			elif tmp <= 0:
				self.__error("Playwright's wait time must be greater than zero")
		self.__args.playwright_wait = tmp

	def __validate_concurrent_requests(self):
		tmp = 30
		if self.__args.concurrent_requests:
			if not self.__args.concurrent_requests.isdigit():
				self.__error("Number of concurrent requests must be numeric")
			else:
				tmp = int(self.__args.concurrent_requests)
				if tmp <= 0:
					self.__error("Number of concurrent requests must be greater than zero")
		self.__args.concurrent_requests = tmp

	def __validate_concurrent_requests_domain(self):
		tmp = 10
		if self.__args.concurrent_requests_domain:
			if not self.__args.concurrent_requests_domain.isdigit():
				self.__error("Number of concurrent requests per domain must be numeric")
			else:
				tmp = int(self.__args.concurrent_requests_domain)
				if tmp <= 0:
					self.__error("Number of concurrent requests per domain must be greater than zero")
		self.__args.concurrent_requests_domain = tmp

	def __validate_sleep(self,):
		tmp = 0
		if self.__args.sleep:
			tmp = general.to_float(self.__args.sleep)
			if tmp is None:
				self.__error("Sleep time between two consecutive requests must be numeric")
			elif tmp <= 0:
				self.__error("Sleep time between two consecutive requests must be greater than zero")
		self.__args.sleep = tmp

	def __validate_auto_throttle(self):
		tmp = 0
		if self.__args.auto_throttle:
			tmp = general.to_float(self.__args.auto_throttle)
			if tmp is None:
				self.__error("Auto throttle must be numeric")
			elif tmp <= 0:
				self.__error("Auto throttle must be greater than zero")
		self.__args.auto_throttle = tmp

	def __validate_retries(self):
		tmp = 2
		if self.__args.retries:
			if not self.__args.retries.isdigit():
				self.__error("Number of retries must be numeric")
			else:
				tmp = int(self.__args.retries)
				if tmp <= 0:
					self.__error("Number of retries must be greater than zero")
		self.__args.retries = tmp

	def __validate_recursion(self):
		tmp = 1
		if self.__args.recursion:
			if not self.__args.recursion.isdigit():
				self.__error("Recursion depth must be numeric")
			else:
				tmp = int(self.__args.recursion)
				if tmp < 0:
					self.__error("Recursion depth must be greater than or equal to zero")
		self.__args.recursion = tmp

	def __validate_request_timeout(self):
		tmp = 60
		if self.__args.request_timeout:
			tmp = general.to_float(self.__args.request_timeout)
			if tmp is None:
				self.__error("Request timeout must be numeric")
			elif tmp <= 0:
				self.__error("Request timeout must be greater than zero")
		self.__args.request_timeout = tmp

	def __validate_header(self):
		tmp = {}
		if self.__args.header:
			for entry in self.__args.header:
				key, value = header.get_key_value(entry[0])
				if not key:
					self.__error(f"Invalid HTTP request header: {entry[0]}")
					continue
				tmp[key] = value
		self.__args.header = tmp

	def __validate_cookie(self):
		tmp = {}
		if self.__args.cookie:
			for entry in self.__args.cookie:
				key, value = cookie.get_key_value(entry[0])
				if not key:
					self.__error(f"Invalid HTTP cookie: {entry[0]}")
					continue
				tmp[key] = value
		self.__args.cookie = tmp

	def __validate_user_agent(self):
		tmp = [config.USER_AGENT]
		if self.__args.user_agent:
			lower = self.__args.user_agent.lower()
			if lower == "random-all":
				tmp = bot_safe_agents.get_all()
			elif lower == "random":
				tmp = [bot_safe_agents.get_random()]
			else:
				tmp = [self.__args.user_agent]
		self.__args.user_agent = tmp

	def __validate_proxy(self):
		if self.__args.proxy:
			success, message = url.validate(self.__args.proxy)
			if not success:
				self.__error(message)

	def __validate_directory(self):
		if self.__args.directory:
			if not directory.is_directory(self.__args.directory):
				self.__error(f"\"{self.__args.directory}\" does not exist or is not a directory")
