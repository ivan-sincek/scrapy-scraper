#!/usr/bin/env python3

import colorama, datetime, termcolor

colorama.init(autoreset = True)

def to_float(value: str):
	"""
	Returns 'None' on failure.
	"""
	tmp = None
	try:
		tmp = float(value)
	except ValueError:
		pass
	return tmp

# ----------------------------------------

def get_timestamp(message: str):
	"""
	Get the current timestamp.
	"""
	return f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}"

def print_error(message: str):
	"""
	Print an error message.
	"""
	print(f"ERROR: {message}")

def print_cyan(message: str):
	"""
	Print a message in cyan color.
	"""
	termcolor.cprint(message, "cyan")

def print_green(message: str):
	"""
	Print a message in green color.
	"""
	termcolor.cprint(message, "green")

def print_yellow(message: str):
	"""
	Print a message in yellow color.
	"""
	termcolor.cprint(message, "yellow")

def print_red(message: str):
	"""
	Print a message in red color.
	"""
	termcolor.cprint(message, "red")
