"""-----------------------------------------------------------------------------

	kijiji_scraper

	This module is responsible for sending requests to kijiji and parsing those
	requests into usable data.

-----------------------------------------------------------------------------"""

import lxml
import lxml.html
import requests
import asyncio
import aiohttp
import time

import client_state


"""-----------------------------------------------------------------------------

	Globals

-----------------------------------------------------------------------------"""

global NORMAL_AD_CLASS
global TOP_AD_CLASS
global THIRD_PARTY_TOP_AD_CLASS
global THIRD_PARTY_NORMAL_AD_CLASS
NORMAL_AD_CLASS = '''"
            search-item
             regular-ad
        "'''
TOP_AD_CLASS = '''"
            search-item
             top-feature 
        "'''

THIRD_PARTY_TOP_AD_CLASS = '''"
            search-item
             cas-channel top-feature  third-party
        "'''
THIRD_PARTY_NORMAL_AD_CLASS = '''"
            search-item
             cas-channel regular-ad third-party
        "'''

global LOCATION_LOOKUP
LOCATION_LOOKUP = {
	'all-of-toronto': {
		'name': 'b-gta-greater-toronto-area',
		'code': 'k0l1700272'
	},
	'city-of-toronto': {
		'name': 'b-city-of-toronto',
		'code': 'k0l1700273'
	}
}

global NUM_PAGES_PER_CYCLE
NUM_PAGES_PER_CYCLE = 5

global CONNECTION_TIMEOUT
CONNECTION_TIMEOUT = 5

global MAX_SCRAPE_TIME
MAX_SCRAPE_TIME = 10


"""-----------------------------------------------------------------------------

	Helper Functions

-----------------------------------------------------------------------------"""

def convert_price_text_to_float(text):
	try:
		# takes the dollar sign off
		return float(text[1::])
	except ValueError:
		return text

def generate_url_elements_from_name_and_location(name, location):
	global LOCATION_LOOKUP
	location_entry = LOCATION_LOOKUP.get(location)
	if location_entry is not None:
		stripped_name = name.strip().lower()
		product_name = stripped_name.replace(" ", "-")
		location_name = location_entry.get('name')
		location_code = location_entry.get('code')
		return {
			'product_name': product_name,
			'location_name': location_name,
			'location_code': location_code
		}
	else:
		raise KeyError("Given location is not a valid location.")

def generate_page_url_from_url_elements(url_elements, page_num):
	product_name = url_elements.get('product_name')
	location_name = url_elements.get('location_name')
	location_code = url_elements.get('location_code')
	if page_num == 1:
		return 'http://kijiji.ca/' + location_name + '/' + product_name + '/' + location_code
	elif page_num > 1:
		page_number = 'page-' + str(page_num)
		return 'http://kijiji.ca/' + location_name + '/' + product_name + '/' + page_number + '/' + location_code
	else:
		raise IndexError("Page number must be a positive integer.")


"""-----------------------------------------------------------------------------

	Parse html Content

-----------------------------------------------------------------------------"""

def get_ads_from_page(tree, class_name):
	ads = tree.findall('.//div[@class=' + class_name + ']')
	dicts = []
	for ad in ads:
		# reading raw string values from html
		info_container = ad.find('.//div[@class="info-container"]')
		raw_title = info_container.find('.//a[@class="title enable-search-navigation-flag "]').text
		raw_price = info_container.find('.//div[@class="price"]').text
		raw_description = info_container.find('.//div[@class="description"]').text
		raw_location = info_container.find('.//div[@class="location"]').text
		# third-party ads have no date given
		raw_date_posted = None
		try:
			raw_date_posted = info_container.find('.//span[@class="date-posted"]').text
		except AttributeError:
			pass
		raw_url = info_container.find('.//a[@class="title enable-search-navigation-flag "]').get('href')
		raw_ad_id = ad.get('data-ad-id')
		# converting raw values into appropriate formats / types
		title = raw_title.strip()
		price = convert_price_text_to_float(raw_price.strip())
		description = raw_description.strip()
		location = raw_location.strip()
		date_posted = raw_date_posted.strip()
		url = 'http://kijiji.ca' + raw_url
		ad_id = int(raw_ad_id)
		dicts.append({
			'title': title,
			'price': price,
			'description': description,
			'location': location,
			'date_posted': date_posted,
			'url': url,
			'ad_id': ad_id,
			'html_class': None
		})
	return dicts

# third party ads have several differences
def get_third_party_ads_from_page(tree, class_name):
	ads = tree.findall('.//div[@class=' + class_name + ']')
	dicts = []
	for ad in ads:
		# reading raw string values from html
		info_container = ad.find('.//div[@class="info-container"]')
		raw_title = info_container.find('.//a[@class="title enable-search-navigation-flag  cas-channel-id"]').text
		raw_price = info_container.find('.//div[@class="price"]').text
		raw_description = info_container.find('.//div[@class="description"]').text
		raw_location = info_container.find('.//div[@class="location"]').text
		# third-party ads have no date given
		raw_date_posted = ''
		raw_url = info_container.find('.//a[@class="title enable-search-navigation-flag  cas-channel-id"]').get('href')
		raw_ad_id = ad.get('data-ad-id')
		# converting raw values into appropriate formats / types
		title = raw_title.strip()
		price = convert_price_text_to_float(raw_price.strip())
		description = raw_description.strip()
		location = raw_location.strip()
		date_posted = raw_date_posted.strip()
		url = 'http://kijiji.ca' + raw_url
		ad_id = int(raw_ad_id)
		dicts.append({
			'title': title,
			'price': price,
			'description': description,
			'location': location,
			'date_posted': date_posted,
			'url': url,
			'ad_id': ad_id,
			'html_class': None
		})

	return dicts

def get_bottom_bar_information(tree):
	bottom_bar = tree.find('.//div[@class="bottom-bar"]')
	page_num = None
	is_final_page = None
	if bottom_bar is None:
		page_num = 1
		is_final_page = True
	else:
		raw_current_page_num = bottom_bar.find('.//span[@class="selected"]').text
		page_num = int(raw_current_page_num)
		next_button = bottom_bar.find('.//a[@title="Next"]')
		is_final_page = next_button is None
	return {
		'page_num': page_num,
		'is_final_page': is_final_page
	}


"""-----------------------------------------------------------------------------

	Asynchronous Requests

-----------------------------------------------------------------------------"""

async def get_ad_page_information(name, location, page_num, info_list):
	global CONNECTION_TIMEOUT
	elements = generate_url_elements_from_name_and_location(name, location)
	url = generate_page_url_from_url_elements(elements, page_num)
	root = None
	async with aiohttp.ClientSession() as client_session:
		with aiohttp.Timeout(CONNECTION_TIMEOUT):
			page = await client_session.get(url)
			html = await page.text()
			root = lxml.html.fromstring(html)
	bottom_bar_information = get_bottom_bar_information(root)
	normal_ads = None
	top_ads = None
	third_party_normal_ads = None
	third_party_top_ads = None
	third_party_ads = None
	try:
		normal_ads = get_ads_from_page(root, NORMAL_AD_CLASS)
		for ad in normal_ads:
			ad['html_class'] = 'normal'
	except SyntaxError:
		normal_ads = []
	try:
		top_ads = get_ads_from_page(root, TOP_AD_CLASS)
		for ad in top_ads:
			ad['html_class'] = 'top'
	except SyntaxError:
		top_ads = []
	try:
		third_party_normal_ads = get_third_party_ads_from_page(root, THIRD_PARTY_NORMAL_AD_CLASS)
		for ad in third_party_normal_ads:
			ad['html_class'] = 'third_party'
	except SyntaxError:
		third_party_normal_ads = []
	try:
		third_party_top_ads = get_third_party_ads_from_page(root, THIRD_PARTY_TOP_AD_CLASS)
		for ad in third_party_top_ads:
			ad['html_class'] = 'third_party'
	except SyntaxError:
		third_party_top_ads = []
	third_party_ads = third_party_top_ads
	third_party_ads.extend(third_party_normal_ads)
	new_entry = {
		'normal_ads': normal_ads,
		'top_ads': top_ads,
		'third_party_ads': third_party_ads,
		'bottom_bar_information': bottom_bar_information
	}
	info_list.append(new_entry)

# return coroutine that requests pages <start> through <end>
def routine_ad_page_information_page_range(parameters, start, end, info_list):
	name = parameters.get('product_name')
	location = parameters.get('location')
	if start <= end:
		li = [get_ad_page_information(
			name = name,
			location = location,
			page_num = x,
			info_list = info_list
		) for x in range(start, end + 1)]
		return asyncio.gather(*li)
	else:
		raise ValueError('Start page num must be less than end page num.')


"""-----------------------------------------------------------------------------

	Public Routines

-----------------------------------------------------------------------------"""

def get_ads_from_ad_list(ad_list, current_ids, incl_func):
	li = [ad for ad in ad_list if incl_func(ad)]
	for ad in li:
		ad_id = ad['ad_id']
		current_ids.add(ad_id)
	return li

# generates list of ad entries based on parameters, mandatory list_check callable,
# and optional filter and post-processing callables
def get_ad_entries_from_constraints(parameters, list_check):
	global MAX_SCRAPE_TIME
	global NUM_PAGES_PER_CYCLE
	# initialising function-level vars
	ad_entries = []
	current_ad_ids = set()
	start_page_num = 1
	# reading in parameters and assigning defaults
	num_pages_per_cycle = parameters.get('num_pages_per_cycle')
	num_pages_per_cycle = num_pages_per_cycle if num_pages_per_cycle is not None else NUM_PAGES_PER_CYCLE
	end_page_num = start_page_num + num_pages_per_cycle - 1
	product_name = parameters.get('product_name')
	location = parameters.get('location')
	entry_incl = parameters.get('entry_incl')
	entry_break = parameters.get('entry_break')
	post_proc = parameters.get('post_proc')
	entry_incl = entry_incl if entry_incl is not None else lambda x:True
	entry_break = entry_break if entry_break is not None else lambda x:False
	post_proc = post_proc if post_proc is not None else lambda x:x
	# loop sentinels
	is_final_page = False
	process_time_out = False
	forced_entry_break = False
	test_cycle = 1
	def incl_function(ad):
		ad_id = ad['ad_id']
		return (ad_id not in current_ad_ids) and entry_incl(ad)
	# stops GET when list_check returns True or on final page
	start = time.perf_counter()
	while (not list_check(ad_entries)) and (not is_final_page) and (not process_time_out) and (not forced_entry_break):
		print('ON CYCLE: ' + str(test_cycle))
		test_cycle += 1
		# get ad information and sorts
		info_list = []
		loop = asyncio.get_event_loop()
		routine = routine_ad_page_information_page_range(parameters, start_page_num, end_page_num, info_list)
		loop.run_until_complete(routine)
		start_page_num += num_pages_per_cycle
		end_page_num += num_pages_per_cycle
		info_list.sort(key = lambda x:x['bottom_bar_information']['page_num'])
		# iterates through list of ads
		for ad_page_information in info_list:
			normal_ads = ad_page_information['normal_ads']
			top_ads = ad_page_information['top_ads']
			third_party_ads = ad_page_information['third_party_ads']
			ad_list = top_ads + normal_ads + third_party_ads
			is_final_page = ad_page_information['bottom_bar_information']['is_final_page']
			ad_page = get_ads_from_ad_list(
				ad_list = ad_list,
				current_ids = current_ad_ids,
				incl_func = incl_function
			)
			early_break_check = map(entry_break, ad_page)
			forced_entry_break = any(early_break_check)
			ad_entries.extend(ad_page)
		# time check
		current_time = time.perf_counter() - start
		process_time_out = current_time >= MAX_SCRAPE_TIME
	return post_proc(ad_entries)


def main():
	ad_entries = get_ad_entries_from_constraints(
		{
			'product_name': 'dafsf',
			'location': 'city-of-toronto',
			'show_top_ads': False,
			'show_third_party_ads': False,
			'only_new_ads': False,
			'entry_incl': lambda x:True,
			'post_proc': lambda x:x[:50]
		},
		list_check = lambda x: len(x) >= 50,
	)
	for ad in ad_entries:
		title = ad.get('title')
		print(title)




if __name__ == "__main__":
	main()