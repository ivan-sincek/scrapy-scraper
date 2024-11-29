#!/usr/bin/env python3

from .utils import config, scrape, validate

def main():
	success, args = validate.Validate().validate_args()
	if success:
		config.banner()
		scrapy_scraper = scrape.ScrapyScraper(
			args.urls,
			args.whitelist,
			args.links,
			args.playwright,
			args.playwright_wait,
			args.concurrent_requests,
			args.concurrent_requests_domain,
			args.sleep,
			args.random_sleep,
			args.auto_throttle,
			args.retries,
			args.recursion,
			args.request_timeout,
			args.header,
			args.cookie,
			args.user_agent,
			args.proxy,
			args.directory,
			args.out,
			args.debug
		)
		scrapy_scraper.run()

if __name__ == "__main__":
	main()
