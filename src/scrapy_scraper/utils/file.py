#!/usr/bin/env python3

from . import array

import os

__ENCODING = "ISO-8859-1"

def is_file(file: str):
	"""
	Returns 'True' if the 'file' exists and is a regular file.
	"""
	return os.path.isfile(file)

def validate(file: str):
	"""
	Validate a file.\n
	Success flag is 'True' if the file has a read permission and is not empty.
	"""
	success = False
	message = ""
	if not os.access(file, os.R_OK):
		message = f"\"{file}\" does not have a read permission"
	elif not os.stat(file).st_size > 0:
		message = f"\"{file}\" is empty"
	else:
		success = True
	return success, message

def read_array(file: str) -> list[str]:
	"""
	Read a file line by line, and append the lines to a list.\n
	Whitespace will be stripped from each line, and empty lines will be removed.\n
	Returns a unique list.
	"""
	tmp = []
	with open(file, "r", encoding = __ENCODING) as stream:
		for line in stream:
			line = line.strip()
			if line:
				tmp.append(line)
	return array.unique(tmp)

def write_array(array: list[str], out: str):
	"""
	Write a list to an output file.\n
	Whitespace will be stripped from each string in the list, and empty strings will be removed.
	"""
	with open(out, "w", encoding = __ENCODING) as stream:
		for entry in array:
			entry = entry.strip()
			if entry:
				stream.write(f"{entry}\n")
