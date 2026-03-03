#!/usr/bin/env python3

import os

def is_directory(directory: str):
	"""
	Returns 'True' if the 'directory' exists and is a regular directory.
	"""
	return os.path.isdir(directory)
