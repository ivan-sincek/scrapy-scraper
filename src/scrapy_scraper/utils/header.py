#!/usr/bin/env python3

import re

def get_key_value(header: str):
	"""
	Get a key-value pair from an HTTP request header.\n
	Returns an empty key-value pair on failure.
	"""
	key = ""; value = ""
	if re.search(r"^[^\:]+\:.+$", header):
		key, value = header.split(":", 1)
	return key.strip(), value.strip()
