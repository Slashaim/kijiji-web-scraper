"""-----------------------------------------------------------------------------

	helpers.py

	Pure functions used for various tasks.

-----------------------------------------------------------------------------"""

import re


"""-----------------------------------------------------------------------------

	Checks
	
-----------------------------------------------------------------------------"""

# check for name made entirely of alphanumerics or spaces
alphanumeric_space_full = re.compile('^[\w ]+$')
def valid_product_name(arg):
	try:
		match = alphanumeric_space_full.match(arg)
		return match is not None
	except TypeError:
		return False

def get_max_ads(arg):
	try:
		max_ads = int(arg)
		return max_ads
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
		nearest_cent = round(arg, 2)
		cents = arg * 100
		if cents % 10 == 0:
			return '$' + str(nearest_cent) + '0'
		else:
			return '$' + str(nearest_cent)
	except TypeError:
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