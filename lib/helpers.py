"""-----------------------------------------------------------------------------

	helpers.py

	Pure functions used for various tasks.

-----------------------------------------------------------------------------"""

import re
import logging

logging.basicConfig(filename = '.program.log', filemode = 'a', format = '%(levelname)s: %(asctime)s: %(message)s')

"""-----------------------------------------------------------------------------

	Conversion Tables

-----------------------------------------------------------------------------"""

ui_to_location = {
	'All of Toronto (GTA)': 'all-of-toronto',
	'Toronto (GTA)': 'all-of-toronto',
	'Canada': 'canada',
	'City of Toronto': 'city-of-toronto',
	'Markham / York Region': 'markham-york-region',
	'Mississauga / Peel Region': 'mississauga-peel-region',
	'Oakville / Halton Region': 'oakville-halton-region',
	'Oshawa / Durham Region': 'oshawa-durham-region'
}

location_to_ui = {
	'canada': 'Canada',
	'all-of-toronto': 'All of Toronto (GTA)',
	'city-of-toronto': 'City of Toronto',
	'markham-york-region': 'Markham / York Region',
	'mississauga-peel-region': 'Mississauga / Peel Region',
	'oakville-halton-region': 'Oakville / Halton Region',
	'oshawa-durham-region': 'Oshawa / Durham Region'
}


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

	Input conversions
	
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

def convert_ui_to_location(ui_location):
	try:
		return ui_to_location[ui_location]
	except IndexError:
		logging.warning("'" + ui_location + "' does not have an associated location.")
		return ''


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

def convert_location_to_ui(location):
	try:
		return location_to_ui[location]
	except:
		logging.warning("'" + location + "' does not have an associated UI display.")
		return ''