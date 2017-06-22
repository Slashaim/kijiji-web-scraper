import lxml
import lxml.html
import requests

# class names of ads
# since Kijiji is weird, it uses a lot of whitespace in the class names
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

# lookup table of valid locations
location_lookup = {
	'all-of-toronto': {
		'name': 'b-gta-greater-toronto-area',
		'code': 'k0l1700272'
	},
	'city-of-toronto': {
		'name': 'b-city-of-toronto',
		'code': 'k0l1700273'
	}
}


def convert_price_text_to_float(text):
	try:
		# takes the dollar sign off
		return float(text[1::])
	except ValueError:
		return text


def generate_url_elements_from_name_and_location(name, location):
	location_entry = location_lookup.get(location)
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


def get_root_element_from_url(url):
	page = requests.get(url)
	return lxml.html.fromstring(page.content)


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


def get_ads(name, location, page_num):
	elements = generate_url_elements_from_name_and_location(name, location)
	url = generate_page_url_from_url_elements(elements, page_num)
	root = get_root_element_from_url(url)
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
	return {
		'normal_ads': normal_ads,
		'top_ads': top_ads,
		'third_party_ads': third_party_ads
	}


def main():
	ads = get_ads('Playstation 4', 'all-of-toronto', 1)
	for ad in ads.get('third_party_ads'):
		print(ad['ad_id'], ad['title'])



if __name__ == "__main__":
	main()