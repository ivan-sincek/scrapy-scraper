#!/usr/bin/env python3

import tldextract, urllib.parse

__URL_SCHEME_WHITELIST = ["http", "https", "socks4", "socks4h", "socks5", "socks5h"]
__MIN_PORT_NUM         = 1
__MAX_PORT_NUM         = 65535

def is_http(url: str):
	return urllib.parse.urlsplit(url).scheme.lower() in ["http", "https"]

def validate(url: str):
	"""
	Validate a URL.
	"""
	success = False
	message = ""
	tmp = urllib.parse.urlsplit(url)
	if not tmp.scheme:
		message = f"URL scheme is required: {url}"
	elif tmp.scheme not in __URL_SCHEME_WHITELIST:
		message = f"Supported URL schemes are 'http[s]', 'socks4[h]', and 'socks5[h]': {url}"
	elif not tmp.netloc:
		message = f"Invalid domain name: {url}"
	elif tmp.port and (tmp.port < __MIN_PORT_NUM or tmp.port > __MAX_PORT_NUM):
		message = f"Port number is out of range: {url}"
	else:
		success = True
	return success, message

def validate_multiple(urls: list[str]):
	"""
	Validate multiple URLs.
	"""
	success = True
	message = ""
	for url in urls:
		success, message = validate(url)
		if not success:
			break
	return success, message

def extract_fqdn(url: str) -> str:
	"""
	Extract the fully qualified domain name from a URL.\n
	Returns an empty string on failure.
	"""
	tmp = ""
	obj = tldextract.extract(url)
	if obj.fqdn:
		tmp = obj.fqdn.lower()
	return tmp

def extract_fqdn_multiple(urls: list[str]) -> list[str]:
	"""
	Extract the fully qualified domain names from a list of URLs.\n
	Returns an empty list on failure.
	"""
	tmp = []
	for url in urls:
		url = extract_fqdn(url)
		if url:
			tmp.append(url)
	return tmp
