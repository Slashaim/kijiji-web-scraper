"""-----------------------------------------------------------------------------

	helpers.py

	Pure functions used for various tasks.

-----------------------------------------------------------------------------"""

import re


"""-----------------------------------------------------------------------------

	Math
	
-----------------------------------------------------------------------------"""

def clamp(val, minimum = None, maximum = None):
	if minimum is not None and maximum is not None:
		if minimum > maximum:
			raise ValueError('Minimum must be less than or equal to maximum.')
		return min(maximum, max(val, minimum))
	elif minimum is not None:
		return max(val, minimum)
	elif maximum is not None:
		return min(val, maximum)
	else:
		return val


"""-----------------------------------------------------------------------------

	Checks
	
-----------------------------------------------------------------------------"""

# check for name made entirely of alphanumerics or spaces
alphanumeric_space_full = re.compile('^[\w ]+$')
def valid_product_name(arg):
	try:
		stripped_str = arg.strip()
		match = alphanumeric_space_full.match(stripped_str)
		return match is not None
	except TypeError:
		return False
	except AttributeError:
		return False


"""-----------------------------------------------------------------------------

	Input conversions (string to other)
	
-----------------------------------------------------------------------------"""

def get_max_ads(arg):
	try:
		max_ads = int(arg)
		if max_ads >= 0:
			return max_ads
		else:
			raise ValueError
	except ValueError:
		return None
	except SyntaxError:
		return None

# returns None for 'no max price' and False for 'invalid max price'
def get_max_price(arg):
	try:
		if len(arg) == 0:
			return None
		else:
			max_price = float(arg)
			if max_price < 0:
				return False
			elif max_price == 0:
				return None
			else:
				return max_price
	except ValueError:
		return False
	except SyntaxError:
		return False


"""-----------------------------------------------------------------------------

	Display conversions
	
-----------------------------------------------------------------------------"""

def convert_price_to_display(arg):
	try:
		nearest_cent = round(float(arg), 2)
		thousands_separated = format(nearest_cent, ',.2f')
		return '$' + thousands_separated
	except TypeError:
		if arg is None:
			return ''
		else:
			return arg
	except ValueError:
		if arg is None:
			return ''
		else:
			return arg

def convert_html_class_to_display(arg):
	if arg == 'normal':
		return 'Normal Ad'
	elif arg == 'top':
		return 'Top Ad'
	elif arg == 'third_party':
		return 'Third Party Ad'
	else:
		return ''