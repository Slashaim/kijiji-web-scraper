"""-----------------------------------------------------------------------------

	gui.py

	Controls the creation of the GUI.
	
-----------------------------------------------------------------------------"""

import wx
import re
import time
import asyncio
import threading
import kijiji_scraper


"""-----------------------------------------------------------------------------

	Globals
	
-----------------------------------------------------------------------------"""

global GUI_ELEMENTS
global VALID_LOCATIONS
global AD_ENTRIES
global NOTIFICATION_ENTRIES
global TRACKER_ENTRIES
global ACTIVE_VIEW
global UI_TO_LOCATION
global LOCATION_TO_UI
global HARD_MAX_AD_NUMBER

GUI_ELEMENTS = {}
VALID_LOCATIONS = [
	'All of Toronto (GTA)',
	'City of Toronto'
]
AD_ENTRIES = []
NOTIFICATION_ENTRIES = []
TRACKER_ENTRIES = []
ACTIVE_VIEW = None
UI_TO_LOCATION = {
	'All of Toronto (GTA)': 'all-of-toronto',
	'City of Toronto': 'city-of-toronto'
}
LOCATION_TO_UI = {
	'all-of-toronto': 'All of Toronto (GTA)',
	'city-of-toronto': 'City of Toronto'
}
HARD_MAX_AD_NUMBER = 50

# global DUMMY
# DUMMY = {
# 	'title': 'Test',
# 	'price': 500.00,
# 	'description': 'Foo',
# 	'location': 'Here',
# 	'date_posted': '5 seconds ago',
# 	'url': 'http://website.org'
# }
# global OTHER_DUMMY
# OTHER_DUMMY = {
# 	'title': 'Example',
# 	'price': 'this is the price',
# 	'description': 'Bar',
# 	'location': 'Not here',
# 	'date_posted': '5 years ago',
# 	'url': 'http://website.org'
# }
# AD_ENTRIES.append(DUMMY)
# AD_ENTRIES.append(OTHER_DUMMY)
# for i in range(0, 30):
# 	AD_ENTRIES.append(DUMMY)

# dummy_notification = {
# 	'notification_type': 'newad',
# 	'front_text': 'New Ad',
# 	'notification_title': 'Title Here',
# 	'ad_price': 500.2,
# 	'ad_title': 'foo',
# 	'ad_url': 'http://website.org'
# }
# other_dummy_notification = {
# 	'notification_type': 'newad',
# 	'front_text': 'New Ad',
# 	'notification_title': 'dlajfkl',
# 	'ad_price': 'iuebn',
# 	'ad_title': 'foo',
# 	'ad_url': 'http://website.org'
# }
# for i in range(0, 30):
# 	if i % 2 == 0:
# 		NOTIFICATION_ENTRIES.append(dummy_notification)
# 	else:
# 		NOTIFICATION_ENTRIES.append(other_dummy_notification)

global USER_PRODUCT_NAME
global USER_MAX_ADS
global USER_LOCATION_INDEX
global USER_MAX_PRICE
USER_PRODUCT_NAME = None
USER_MAX_ADS = None
USER_LOCATION_INDEX = None
USER_MAX_PRICE = None

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

def get_notification_title_from_newad(entry):
	product_name = entry.get('product_name')
	location = LOCATION_TO_UI[entry.get('location')]
	given_max_price = entry.get('max_price')
	max_price = convert_price_to_display(given_max_price)
	if given_max_price:
		return product_name + ' in ' + location + ' under ' + max_price
	else:
		return product_name + ' in ' + location


"""-----------------------------------------------------------------------------

	App creation
	
-----------------------------------------------------------------------------"""

def create_app():
	app = wx.App(False)
	return app


"""-----------------------------------------------------------------------------

	Views Options creation
	
-----------------------------------------------------------------------------"""

def create_views_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_views_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_views_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Change Views", style = wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_NONE)
	return label

def scrape_mode_button_callback(arg):
	change_view('scraping')

def create_scrape_mode_button(parent):
	button = wx.Button(parent, wx.ID_ANY, "Scraping View")
	button.Bind(wx.EVT_BUTTON, scrape_mode_button_callback)
	return button

def notifications_mode_button_callback(arg):
	change_view('notifications')

def create_notifications_mode_button(parent):
	button = wx.Button(parent, wx.ID_ANY, "Notifications View")
	button.Bind(wx.EVT_BUTTON, notifications_mode_button_callback)
	return button

def trackers_mode_button_callback(arg):
	change_view('trackers')

def create_trackers_mode_button(parent):
	button = wx.Button(parent, wx.ID_ANY, "Trackers View")
	button.Bind(wx.EVT_BUTTON, trackers_mode_button_callback)
	return button

def generate_views_options(parent):
	global GUI_ELEMENTS
	# creating panel and setting sizer
	views_panel = create_views_panel(parent)
	views_sizer = create_views_sizer()
	views_panel.SetSizer(views_sizer)
	# creating elements
	views_label = create_views_label(views_panel)
	scrape_mode_button = create_scrape_mode_button(views_panel)
	notifications_mode_button = create_notifications_mode_button(views_panel)
	trackers_mode_button = create_trackers_mode_button(views_panel)
	# adding to sizer
	views_sizer.Add(views_label, 0, wx.ALL|wx.EXPAND)
	views_sizer.Add(scrape_mode_button, 0, wx.ALL|wx.EXPAND, 5)
	views_sizer.Add(notifications_mode_button, 0, wx.ALL|wx.EXPAND, 5)
	views_sizer.Add(trackers_mode_button, 0, wx.ALL|wx.EXPAND, 5)
	GUI_ELEMENTS['views_options_panel'] = views_panel
	return views_panel


"""-----------------------------------------------------------------------------

	Scrape Options creation
	
-----------------------------------------------------------------------------"""

def create_scrape_options_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_scrape_options_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_scrape_options_horizontal_sizer():
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	return sizer

def create_scrape_options_sub_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_scrape_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Scraping", style = wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_NONE)
	return label

def create_product_name_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Search:", style = wx.TE_READONLY|wx.BORDER_NONE)
	return label

def create_product_name_text_box(parent):
	global GUI_ELEMENTS
	global USER_PRODUCT_NAME
	startingText = USER_PRODUCT_NAME or ''
	text_box = wx.TextCtrl(parent, wx.ID_ANY, startingText)
	GUI_ELEMENTS['product_name_text_box'] = text_box
	return text_box

def create_only_new_checkbox(parent):
	checkbox = wx.CheckBox(parent, wx.ID_ANY, "Only scrape new ads")
	GUI_ELEMENTS['only_new_checkbox'] = checkbox
	return checkbox

def create_max_ads_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Max Ads Shown:", style = wx.TE_READONLY|wx.TE_RIGHT|wx.BORDER_NONE)
	return label

def create_max_ads_text_box(parent):
	global GUI_ELEMENTS
	global HARD_MAX_AD_NUMBER
	startingText = str(USER_MAX_ADS or HARD_MAX_AD_NUMBER)
	textbox = wx.TextCtrl(parent, wx.ID_ANY, startingText)
	GUI_ELEMENTS['max_ads_text_box'] = textbox
	return textbox

def create_max_price_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Display if below price:", style = wx.TE_READONLY|wx.TE_RIGHT|wx.BORDER_NONE)
	return label

def create_max_price_text_box(parent):
	global GUI_ELEMENTS
	textbox = wx.TextCtrl(parent, wx.ID_ANY, '')
	GUI_ELEMENTS['max_price_text_box'] = textbox
	return textbox

def create_show_top_ads_checkbox(parent):
	global GUI_ELEMENTS
	checkbox = wx.CheckBox(parent, wx.ID_ANY, "Show Top Ads")
	GUI_ELEMENTS['show_top_ads_checkbox'] = checkbox
	return checkbox

def create_show_third_party_ads_checkbox(parent):
	global GUI_ELEMENTS
	checkbox = wx.CheckBox(parent, wx.ID_ANY, "Show Third-Party Ads")
	GUI_ELEMENTS['show_third_party_ads_checkbox'] = checkbox
	return checkbox

def create_location_choice(parent):
	global GUI_ELEMENTS
	global VALID_LOCATIONS
	global USER_LOCATION_INDEX
	startingChoice = USER_LOCATION_INDEX or 0
	choice = wx.Choice(parent, wx.ID_ANY, choices = VALID_LOCATIONS)
	choice.SetSelection(startingChoice)
	GUI_ELEMENTS['location_choice'] = choice
	return choice

def scrape_button_callback(arg):
	global GUI_ELEMENTS
	global AD_ENTRIES
	global USER_PRODUCT_NAME
	global USER_MAX_ADS
	global USER_LOCATION_INDEX
	global USER_MAX_PRICE
	product_name_text_box = GUI_ELEMENTS['product_name_text_box']
	location_choice = GUI_ELEMENTS['location_choice']
	scrape_message = GUI_ELEMENTS['scrape_message']
	max_ads_text_box = GUI_ELEMENTS['max_ads_text_box']
	max_price_text_box = GUI_ELEMENTS['max_price_text_box']
	only_new_checkbox = GUI_ELEMENTS['only_new_checkbox']
	show_top_ads_checkbox = GUI_ELEMENTS['show_top_ads_checkbox']
	show_third_party_ads_checkbox = GUI_ELEMENTS['show_third_party_ads_checkbox']
	# setting initial gui state
	product_name_text_box.SetBackgroundColour(wx.Colour(255, 255, 255))
	max_ads_text_box.SetBackgroundColour(wx.Colour(255, 255, 255))
	max_price_text_box.SetBackgroundColour(wx.Colour(255, 255, 255))
	product_name_text_box.Refresh()
	max_ads_text_box.Refresh()
	max_price_text_box.Refresh()
	scrape_message.SetValue('')
	# getting initial gui state and checking for valid inputs
	given_product_name = product_name_text_box.GetLineText(lineNo = 0)
	given_max_ads = get_max_ads(max_ads_text_box.GetLineText(lineNo = 0))
	given_max_price = get_max_price(max_price_text_box.GetLineText(lineNo = 0))
	given_location = location_choice.GetSelection()
	location = UI_TO_LOCATION.get(location_choice.GetString(given_location))
	if not valid_product_name(given_product_name):
		scrape_message.SetValue('Invalid product name. Only alphabetical and numeric characters are supported.')
		product_name_text_box.SetBackgroundColour(wx.Colour(255, 240, 240))
		product_name_text_box.Refresh()
		return
	if not given_max_ads or not 1 <= given_max_ads <= HARD_MAX_AD_NUMBER:
		max_ads_text_box.SetBackgroundColour(wx.Colour(255, 240, 240))
		max_ads_text_box.Refresh()
		scrape_message.SetValue('Invalid maximum ad number. Must be between 1 and ' + str(HARD_MAX_AD_NUMBER) + '.')
		return
	if given_max_price is False:
		max_price_text_box.SetBackgroundColour(wx.Colour(255, 240, 240))
		max_price_text_box.Refresh()
		scrape_message.SetValue('Invalid maximum price.')
		return
	if not location:
		scrape_message.SetValue('Invalid location.')
		return
	USER_PRODUCT_NAME = given_product_name
	USER_MAX_ADS = given_max_ads
	USER_LOCATION_INDEX = given_location
	USER_MAX_PRICE = given_max_price
	only_new_ads = only_new_checkbox.GetValue()
	show_top_ads = show_top_ads_checkbox.GetValue()
	show_third_party_ads = show_third_party_ads_checkbox.GetValue()
	# updating AD_ENTRIES
	def list_check(ad_list):
		return len(ad_list) >= given_max_ads

	def entry_incl(ad):
		# determining if class allowed
		html_class = ad.get('html_class')
		cond_a = html_class == 'normal'
		cond_b = html_class == 'top' and show_top_ads
		cond_c = html_class == 'third_party' and show_third_party_ads
		class_allowed = cond_a or cond_b or cond_c
		# determining if price allowed
		price_allowed = True
		price = ad.get('price')
		if given_max_price:
			try:
				price_allowed = price <= given_max_price
			except TypeError:
				price_allowed = False
		return class_allowed and price_allowed

	def post_proc(ad_list):
		return ad_list[:given_max_ads]

	try:
		AD_ENTRIES = kijiji_scraper.get_ad_entries_from_constraints(
			parameters = {
				'product_name': given_product_name,
				'location': location,
				'show_top_ads': show_top_ads,
				'show_third_party_ads': show_third_party_ads,
				'only_new_ads': only_new_ads,
				'entry_incl': entry_incl,
				'post_proc': post_proc		
			},
			list_check = list_check
		)
		update_scrape_view()
	except asyncio.TimeoutError:
		scrape_message.SetValue('Connection timed out. Check internet connectivity or try again later.')

def create_scrape_button(parent):
	global GUI_ELEMENTS
	button = wx.Button(parent, wx.ID_ANY, "Scrape")
	button.Bind(wx.EVT_BUTTON, scrape_button_callback)
	GUI_ELEMENTS['scrape_button'] = button
	return button

def create_scrape_message(parent):
	global GUI_ELEMENTS
	label = wx.TextCtrl(parent, wx.ID_ANY, "", style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
	label.SetBackgroundColour(wx.Colour(240,240,240))
	GUI_ELEMENTS['scrape_message'] = label
	return label

def generate_scrape_options(parent):
	global GUI_ELEMENTS
	# creating panels and setting sizers
	scrape_options_panel = create_scrape_options_panel(parent)
	scrape_options_sizer = create_scrape_options_sizer()
	scrape_options_panel.SetSizer(scrape_options_sizer)
	subpanel_1 = create_scrape_options_sub_panel(scrape_options_panel)
	subpanel_2 = create_scrape_options_sub_panel(scrape_options_panel)
	subpanel_3 = create_scrape_options_sub_panel(scrape_options_panel)
	horiz_sizer_1 = create_scrape_options_horizontal_sizer()
	horiz_sizer_2 = create_scrape_options_horizontal_sizer()
	horiz_sizer_3 = create_scrape_options_horizontal_sizer()
	subpanel_1.SetSizer(horiz_sizer_1)
	subpanel_2.SetSizer(horiz_sizer_2)
	subpanel_3.SetSizer(horiz_sizer_3)
	# creating elements
	scrape_label = create_scrape_label(scrape_options_panel)
	product_name_label = create_product_name_label(subpanel_1)
	product_name_text_box = create_product_name_text_box(subpanel_1)
	only_new_checkbox = create_only_new_checkbox(scrape_options_panel)
	max_ads_label = create_max_ads_label(subpanel_2)
	max_ads_text_box = create_max_ads_text_box(subpanel_2)
	max_price_label = create_max_price_label(subpanel_3)
	max_price_text_box = create_max_price_text_box(subpanel_3)
	show_top_ads_checkbox = create_show_top_ads_checkbox(scrape_options_panel)
	show_third_party_ads_checkbox = create_show_third_party_ads_checkbox(scrape_options_panel)
	location_choice = create_location_choice(scrape_options_panel)
	scrape_button = create_scrape_button(scrape_options_panel)
	scrape_message = create_scrape_message(scrape_options_panel)
	# putting in sizers
	horiz_sizer_1.Add(product_name_label, 0, wx.TOP|wx.EXPAND, 4)
	horiz_sizer_1.Add(product_name_text_box, 1, wx.LEFT|wx.EXPAND, 5)
	horiz_sizer_2.Add(max_ads_label, 0, wx.TOP|wx.EXPAND, 4)
	horiz_sizer_2.Add(max_ads_text_box, 1, wx.LEFT|wx.EXPAND, 5)
	horiz_sizer_3.Add(max_price_label, 0, wx.TOP|wx.EXPAND, 4)
	horiz_sizer_3.Add(max_price_text_box, 1, wx.LEFT|wx.EXPAND, 5)
	scrape_options_sizer.Add(scrape_label, 0, wx.ALL|wx.EXPAND)
	scrape_options_sizer.Add(subpanel_1, 0, wx.ALL|wx.EXPAND, 5)
	scrape_options_sizer.Add(subpanel_2, 0, wx.ALL|wx.EXPAND, 5)
	scrape_options_sizer.Add(subpanel_3, 0, wx.ALL|wx.EXPAND, 5)
	scrape_options_sizer.Add(only_new_checkbox, 0, wx.ALL|wx.EXPAND, 5)
	scrape_options_sizer.Add(show_top_ads_checkbox, 0, wx.ALL|wx.EXPAND, 5)
	scrape_options_sizer.Add(show_third_party_ads_checkbox, 0, wx.ALL|wx.EXPAND, 5)
	scrape_options_sizer.Add(location_choice, 0, wx.ALL|wx.EXPAND, 5)
	scrape_options_sizer.Add(scrape_button, 0, wx.ALL|wx.EXPAND, 5)
	scrape_options_sizer.Add(scrape_message, 0, wx.ALL|wx.EXPAND, 5)
	GUI_ELEMENTS['scrape_options_panel'] = scrape_options_panel
	return scrape_options_panel
	

"""-----------------------------------------------------------------------------

	Notifications Options creation
	
-----------------------------------------------------------------------------"""

def create_notifications_options_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_notifications_options_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_notifications_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Notifications", style = wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_NONE)
	return label

def clear_all_notifications_button_callback(arg):
	global NOTIFICATION_ENTRIES
	NOTIFICATION_ENTRIES = []
	update_notifications_view()

def create_clear_all_notifications_button(parent):
	global GUI_ELEMENTS
	button = wx.Button(parent, wx.ID_ANY, "Clear All Notifications")
	button.Bind(wx.EVT_BUTTON, clear_all_notifications_button_callback)
	GUI_ELEMENTS['clear_all_notifications_button'] = button
	return button

def generate_notifications_options(parent):
	global GUI_ELEMENTS
	# creating panel and setting sizer
	notifications_options_panel = create_notifications_options_panel(parent)
	notifications_options_sizer = create_notifications_options_sizer()
	notifications_options_panel.SetSizer(notifications_options_sizer)
	# creating elements
	notifications_label = create_notifications_label(notifications_options_panel)
	clear_all_notifications_button = create_clear_all_notifications_button(notifications_options_panel)
	# putting in sizers
	notifications_options_sizer.Add(notifications_label, 0, wx.ALL|wx.EXPAND)
	notifications_options_sizer.Add(clear_all_notifications_button, 0, wx.ALL|wx.EXPAND, 5)
	GUI_ELEMENTS['notifications_options_panel'] = notifications_options_panel
	return notifications_options_panel


"""-----------------------------------------------------------------------------

	Trackers Options creation
	
-----------------------------------------------------------------------------"""

def create_trackers_options_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_trackers_options_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_trackers_options_sub_panel_sizer():
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	return sizer

def create_trackers_options_sub_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_trackers_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Trackers", style = wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_NONE)
	return label

def create_tracker_product_name_text_box_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Product Name:", style = wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_NONE)
	return label

def create_tracker_product_name_text_box(parent):
	global GUI_ELEMENTS
	text_box = wx.TextCtrl(parent, wx.ID_ANY)
	GUI_ELEMENTS['tracker_product_name_text_box'] = text_box
	return text_box

def create_tracker_max_price_text_box_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Max Price:", style = wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_NONE)
	return label

def create_tracker_max_price_text_box(parent):
	global GUI_ELEMENTS
	text_box = wx.TextCtrl(parent, wx.ID_ANY)
	GUI_ELEMENTS['tracker_max_price_text_box'] = text_box
	return text_box

def create_tracker_location_choice(parent):
	global GUI_ELEMENTS
	global VALID_LOCATIONS
	choice = wx.Choice(parent, wx.ID_ANY, choices = VALID_LOCATIONS)
	choice.SetSelection(0)
	GUI_ELEMENTS['tracker_location_choice'] = choice
	return choice

def tracker_button_callback(arg):
	global GUI_ELEMENTS
	global TRACKER_ENTRIES
	tracker_product_name_text_box = GUI_ELEMENTS['tracker_product_name_text_box']
	tracker_max_price_text_box = GUI_ELEMENTS['tracker_max_price_text_box']
	tracker_location_choice = GUI_ELEMENTS['tracker_location_choice']
	tracker_message = GUI_ELEMENTS['tracker_message']
	# setting initial gui state
	tracker_product_name_text_box.SetBackgroundColour(wx.Colour(255, 255, 255))
	tracker_product_name_text_box.Refresh()
	tracker_message.SetValue('')
	# getting initial gui state and checking for valid inputs
	given_product_name = tracker_product_name_text_box.GetLineText(lineNo = 0)
	given_max_price = get_max_price(max_price_text_box.GetLineText(lineNo = 0))
	given_location = tracker_location_choice.GetSelection()
	location = UI_TO_LOCATION.get(location_choice.GetString(given_location))
	if not valid_product_name(given_product_name):
		product_name_text_box.SetBackgroundColour(wx.Colour(255, 240, 240))
		product_name_text_box.Refresh()
		tracker_message.SetValue('Invalid product name. Only alphabetical and numeric characters are supported.')
		return
	if given_max_price is False:
		tracker_max_price_text_box.SetBackgroundColour(wx.Colour(255, 240, 240))
		tracker_max_price_text_box.Refresh()
		tracker_message.SetValue('Invalid maximum price.')
		return
	if not location:
		tracker_message.SetValue('Invalid location.')
		return
	# adding new tracker
	add_tracker_entry({
		'product_name': given_product_name,
		'location': location,
		'cycle_time': 900
	})

def create_tracker_button(parent):
	global GUI_ELEMENTS
	button = wx.Button(parent, wx.ID_ANY, "Create New Tracker")
	button.Bind(wx.EVT_BUTTON, tracker_button_callback)
	GUI_ELEMENTS['tracker_button'] = button
	return button

def create_show_tray_notifications_checkbox(parent):
	global GUI_ELEMENTS
	checkbox = wx.CheckBox(parent, wx.ID_ANY, "Show Tray Notifications")
	GUI_ELEMENTS['show_tray_notifications'] = checkbox
	return checkbox

def create_tracker_message(parent):
	global GUI_ELEMENTS
	label = wx.TextCtrl(parent, wx.ID_ANY, "", style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
	label.SetBackgroundColour(wx.Colour(240,240,240))
	GUI_ELEMENTS['tracker_message'] = label
	return label

def generate_trackers_options(parent):
	global GUI_ELEMENTS
	# creating panels and setting sizers
	trackers_options_panel = create_trackers_options_panel(parent)
	trackers_options_sizer = create_trackers_options_sizer()
	trackers_options_panel.SetSizer(trackers_options_sizer)
	subpanel_1 = create_trackers_options_sub_panel(trackers_options_panel)
	subpanel_2 = create_trackers_options_sub_panel(trackers_options_panel)
	horiz_sizer_1 = create_trackers_options_sub_panel_sizer()
	horiz_sizer_2 = create_trackers_options_sub_panel_sizer()
	subpanel_1.SetSizer(horiz_sizer_1)
	subpanel_2.SetSizer(horiz_sizer_2)
	# creating elements
	trackers_label = create_trackers_label(trackers_options_panel)
	tracker_product_name_text_box_label = create_tracker_product_name_text_box_label(subpanel_1)
	tracker_product_name_text_box = create_tracker_product_name_text_box(subpanel_1)
	tracker_max_price_text_box_label = create_tracker_max_price_text_box_label(subpanel_2)
	tracker_max_price_text_box = create_tracker_max_price_text_box(subpanel_2)
	tracker_location_choice = create_tracker_location_choice(trackers_options_panel)
	tracker_button = create_tracker_button(trackers_options_panel)
	show_tray_notifications_checkbox = create_show_tray_notifications_checkbox(trackers_options_panel)
	tracker_message = create_tracker_message(trackers_options_panel)
	# putting in sizers
	horiz_sizer_1.Add(tracker_product_name_text_box_label, 0, wx.TOP|wx.EXPAND, 4)
	horiz_sizer_1.Add(tracker_product_name_text_box, 1, wx.LEFT|wx.EXPAND, 5)
	horiz_sizer_2.Add(tracker_max_price_text_box_label, 0, wx.TOP|wx.EXPAND, 4)
	horiz_sizer_2.Add(tracker_max_price_text_box, 1, wx.LEFT|wx.EXPAND, 5)
	trackers_options_sizer.Add(trackers_label, 0, wx.ALL|wx.EXPAND)
	trackers_options_sizer.Add(subpanel_1, 0, wx.ALL|wx.EXPAND, 5)
	trackers_options_sizer.Add(subpanel_2, 0, wx.ALL|wx.EXPAND, 5)
	trackers_options_sizer.Add(tracker_location_choice, 0, wx.ALL|wx.EXPAND, 5)
	trackers_options_sizer.Add(tracker_button, 0, wx.ALL|wx.EXPAND, 5)
	trackers_options_sizer.Add(show_tray_notifications_checkbox, 0, wx.ALL|wx.EXPAND, 5)
	trackers_options_sizer.Add(tracker_message, 0, wx.ALL|wx.EXPAND, 5)
	GUI_ELEMENTS['trackers_options_panel'] = trackers_options_panel
	return trackers_options_panel


"""-----------------------------------------------------------------------------

	Trackers Options actions
	
-----------------------------------------------------------------------------"""

def add_tracker_entry(tracker_dict):
	global TRACKER_ENTRIES
	entry = {
		'product_name': tracker_dict.get('product_name'),
		'location': tracker_dict.get('location'),
		'max_price': tracker_dict.get('max_price'),
		'start_time': time.perf_counter(),
		'last_scrape_time': 0,
		'active_time': 0,
		'time_to_next_scrape': 0,
		'cycle_time': tracker_dict.get('cycle_time'),
		'scrape_on_next': False,
		'viewed_ad_ids': set()
	}
	TRACKER_ENTRIES.append(entry)

def time_update_tracker_entry(entry):
	current_time = time.perf_counter()
	start_time = entry['start_time']
	last_scrape_time = entry['last_scrape_time']
	cycle_time = entry['cycle_time']
	entry['active_time'] = current_time - start_time
	entry['time_to_next_scrape'] = (last_scrape_time + cycle_time) - current_time
	if (current_time - last_scrape_time) > cycle_time:
		entry['scrape_on_next'] = True

def get_new_ads_for_notifications(entry):
	product_name = entry.get('product_name')
	location = entry.get('location')
	max_price = entry.get('max_price')
	viewed_ad_ids = entry.get('viewed_ad_ids')
	def list_check(li):
		for entry in li:
			if entry in viewed_ad_ids:
				return True
		return False

	def post_proc(li):
		return [x for x in li if x['ad_id'] not in viewed_ad_ids]

	def entry_incl(ad):
		# determining if class allowed
		html_class = ad.get('html_class')
		class_allowed = html_class == 'normal'
		# determining if price allowed
		price_allowed = True
		price = ad.get('price')
		if given_max_price:
			try:
				price_allowed = price <= given_max_price
			except TypeError:
				price_allowed = False
		return class_allowed and price_allowed
	try:
		ads = kijiji_scraper.get_ad_entries_from_constraints(
			parameters = {
				'product_name': product_name,
				'location': location,
				'show_top_ads': False,
				'show_third_party_ads': False,
				'only_new_ads': True,
				'post_proc': post_proc
			},
			list_check = list_check
		)
		return ads
	except asyncio.TimeoutError:
		return []

# may need to do this in a separate thread
def ad_update_tracker_entry(entry):
	global ACTIVE_VIEW
	global NOTIFICATION_ENTRIES
	product_name = entry['product_name']
	location = LOCATION_TO_UI[entry['location']]
	viewed_ads = entry['viewed_ads']
	given_max_price = entry.get('max_price')
	max_price = convert_price_to_display(entry.get('max_price'))
	scrape_on_next = entry['scrape_on_next']
	if scrape_on_next:
		ads = get_new_ads_for_notifications(entry)
		for ad in ads:
			viewed_ads.add(ad)
			notification_title = get_notification_title_from_newad(ad)
			ad_price = convert_price_to_display(ad.get('price'))
			ad_title = ad.get('title')
			ad_url = ad.get('url')
			NOTIFICATION_ENTRIES.append({
				'notification_type': 'newad',
				'front_text': 'New Ad',
				'notification_title': notification_title,
				'ad_price': ad_price,
				'ad_title': ad_title,
				'ad_url': ad_url
			})
		if len(ads) > 0: 
			# if SEND_TRAY_NOTIFICATIONS
			if ACTIVE_VIEW == 'notifications':
				update_notifications_view()





"""-----------------------------------------------------------------------------

	Options Panel creation
	
-----------------------------------------------------------------------------"""

def create_options_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_options_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY, size = (300, 10000))
	return panel

def generate_options_panel(parent):
	global GUI_ELEMENTS
	# setting up panel and sizer
	options_panel = create_options_panel(parent)
	options_sizer = create_options_panel_sizer()
	options_panel.SetSizer(options_sizer)
	GUI_ELEMENTS['options_panel'] = options_panel
	GUI_ELEMENTS['options_panel_sizer'] = options_sizer
	return options_panel


"""-----------------------------------------------------------------------------

	Options Panel actions
	
-----------------------------------------------------------------------------"""

def change_options_panel_state(new_view):
	global GUI_ELEMENTS
	options_panel = GUI_ELEMENTS['options_panel']
	options_sizer = GUI_ELEMENTS['options_panel_sizer']
	options_sizer.Clear(delete_windows = True)
	views_options = generate_views_options(options_panel)
	options_sizer.Add(views_options, 0, wx.ALL|wx.EXPAND)
	options_sizer.AddSpacer(20)
	if new_view == 'scraping':
		scraping_options = generate_scrape_options(options_panel)
		options_sizer.Add(scraping_options, 0, wx.ALL|wx.EXPAND)
	elif new_view == 'notifications':
		notifications_options = generate_notifications_options(options_panel)
		options_sizer.Add(notifications_options, 0, wx.ALL|wx.EXPAND)
	elif new_view == 'trackers':
		trackers_options = generate_trackers_options(options_panel)
		options_sizer.Add(trackers_options, 0, wx.ALL|wx.EXPAND)


"""-----------------------------------------------------------------------------

	Scrape View creation

-----------------------------------------------------------------------------"""

def create_scrape_view_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_scrape_view_panel(parent):
	global GUI_ELEMENTS
	panel = wx.Panel(parent, wx.ID_ANY)
	GUI_ELEMENTS['scrape_view_panel'] = panel
	return panel

def create_ads_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_ads_panel(parent):
	global GUI_ELEMENTS
	panel = wx.ScrolledCanvas(parent, wx.ID_ANY, style = wx.VSCROLL)
	panel.SetScrollbars(1, 40, 1, 40)
	GUI_ELEMENTS['ads_panel'] = panel
	return panel

def create_ad_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_ad_horizontal_sizer():
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	return sizer

def create_scrape_header_text(parent):
	global AD_ENTRIES
	num_ads = len(AD_ENTRIES)
	displayed = str(num_ads) + ' ads found.'
	text = wx.TextCtrl(parent, wx.ID_ANY, displayed, style = wx.BORDER_NONE|wx.TE_READONLY)
	return text

def create_ad_panel(parent, highlight = False):
	panel = None
	if highlight:
		panel = wx.Panel(parent, wx.ID_ANY, style = wx.BORDER_SIMPLE, size = (0, 110))
	else:
		panel = wx.Panel(parent, wx.ID_ANY, style = wx.BORDER_NONE, size = (0, 110))
	return panel

def create_ad_sub_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_ad_html_class(parent, ad_class):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	textbox = wx.TextCtrl(parent, wx.ID_ANY, ad_class, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_RICH|wx.TE_RIGHT)
	textbox.SetBackgroundColour(wx.Colour(240,240,240))
	textbox.SetStyle(0, 500, attr)
	return textbox

def create_ad_title(parent, ad_title):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	textbox = wx.TextCtrl(parent, wx.ID_ANY, ad_title, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_RICH)
	textbox.SetBackgroundColour(wx.Colour(240,240,240))
	textbox.SetStyle(0, 500, attr)
	return textbox

def create_ad_price(parent, ad_price):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	textbox = wx.TextCtrl(parent, wx.ID_ANY, ad_price, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_RICH)
	textbox.SetBackgroundColour(wx.Colour(240,240,240))
	textbox.SetStyle(0, 500, attr)
	return textbox

def create_ad_date_posted(parent, ad_date_posted):
	textbox = wx.TextCtrl(parent, wx.ID_ANY, ad_date_posted, style = wx.TE_READONLY|wx.BORDER_NONE)
	return textbox

def create_ad_location(parent, ad_location):
	textbox = wx.TextCtrl(parent, wx.ID_ANY, ad_location, style = wx.TE_READONLY|wx.BORDER_NONE)
	return textbox

def create_ad_url(parent, ad_url):
	textbox = wx.TextCtrl(parent, wx.ID_ANY, ad_url, style = wx.TE_READONLY|wx.BORDER_NONE|wx.ALIGN_RIGHT)
	textbox.SetBackgroundColour(wx.Colour(240, 240, 240))
	return textbox

def create_ad_description(parent, ad_description):
	textbox = wx.TextCtrl(parent, wx.ID_ANY, ad_description, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
	textbox.SetBackgroundColour(wx.Colour(240,240,240))
	return textbox

def generate_ad_panel(parent, ad_dict):
	# converting dict entries to strings
	title = ad_dict.get('title')
	price = convert_price_to_display(ad_dict.get('price'))
	date_posted = ad_dict.get('date_posted')
	location = ad_dict.get('location')
	url = ad_dict.get('url')
	description = ad_dict.get('description')
	html_class = convert_html_class_to_display(ad_dict.get('html_class'))
	# setting up panel, sub-panels, and sizers
	ad_sizer = create_ad_panel_sizer()
	horiz_sizer_1 = create_ad_horizontal_sizer()
	horiz_sizer_2 = create_ad_horizontal_sizer()
	horiz_sizer_3 = create_ad_horizontal_sizer()
	panel = create_ad_panel(parent)
	subpanel_1 = create_ad_sub_panel(panel)
	subpanel_2 = create_ad_sub_panel(panel)
	subpanel_3 = create_ad_sub_panel(panel)
	panel.SetSizer(ad_sizer)
	subpanel_1.SetSizer(horiz_sizer_1)
	subpanel_2.SetSizer(horiz_sizer_2)
	subpanel_3.SetSizer(horiz_sizer_3)
	# adding price, title, and ad type
	ad_title = create_ad_title(subpanel_1, title)
	ad_price = create_ad_price(subpanel_1, price)
	ad_html_class = create_ad_html_class(subpanel_1, html_class)
	horiz_sizer_1.Add(ad_price, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_1.Add(ad_title, 5, wx.ALL|wx.EXPAND)
	horiz_sizer_1.Add(ad_html_class, 1, wx.ALL|wx.EXPAND)
	# adding date posted, location, and url
	ad_date_posted = create_ad_date_posted(subpanel_2, date_posted)
	ad_location = create_ad_location(subpanel_2, location)
	ad_url = create_ad_url(subpanel_2, url)
	horiz_sizer_2.Add(ad_date_posted, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_2.Add(ad_location, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_2.Add(ad_url, 5, wx.ALL|wx.EXPAND)
	# adding description
	ad_description = create_ad_description(subpanel_3, description)
	horiz_sizer_3.Add(ad_description, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_3.AddStretchSpacer(1)
	# adding all to main sizer
	ad_sizer.Add(subpanel_1, 0, wx.ALL|wx.EXPAND, 5)
	ad_sizer.Add(subpanel_2, 0, wx.ALL|wx.EXPAND, 5)
	ad_sizer.Add(subpanel_3, 0, wx.ALL|wx.EXPAND, 5)
	return panel

def generate_scrape_view(parent):
	global AD_ENTRIES
	scrape_view_sizer = create_scrape_view_sizer()
	scrape_view_panel = create_scrape_view_panel(parent)
	scrape_view_panel.SetSizer(scrape_view_sizer)
	ads_panel_sizer = create_ads_panel_sizer()
	ads_panel = create_ads_panel(scrape_view_panel)
	ads_panel.SetSizer(ads_panel_sizer)
	scrape_header_text = create_scrape_header_text(scrape_view_panel)
	scrape_view_sizer.Add(scrape_header_text, 0, wx.ALL|wx.EXPAND, 5)
	scrape_view_sizer.Add(ads_panel, 1, wx.ALL|wx.EXPAND, 5)
	for ad in AD_ENTRIES:
		ad_panel = generate_ad_panel(ads_panel, ad)
		ads_panel_sizer.Add(ad_panel, 0, wx.ALL|wx.EXPAND, 5)
	return scrape_view_panel

def destroy_scrape_view():
	global GUI_ELEMENTS
	GUI_ELEMENTS['scrape_view_panel'].Destroy()

def update_scrape_view():
	global GUI_ELEMENTS
	main_frame = GUI_ELEMENTS['main_frame']
	main_frame_sizer = GUI_ELEMENTS['main_frame_sizer']
	destroy_scrape_view()
	scrape_view = generate_scrape_view(main_frame)
	main_frame_sizer.Add(scrape_view, 1, wx.ALL|wx.EXPAND)
	main_frame.Layout()

def show_scrape_view():
	global GUI_ELEMENTS
	GUI_ELEMENTS['scrape_view_panel'].Show()

def hide_scrape_view():
	global GUI_ELEMENTS
	GUI_ELEMENTS['scrape_view_panel'].Hide()


"""-----------------------------------------------------------------------------

	Notifications View creation

-----------------------------------------------------------------------------"""

def create_notifications_view_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_notifications_view_panel(parent):
	global GUI_ELEMENTS
	panel = wx.Panel(parent, wx.ID_ANY)
	GUI_ELEMENTS['notifications_view_panel'] = panel
	return panel

def create_notifications_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_notifications_panel(parent):
	global GUI_ELEMENTS
	panel = wx.ScrolledCanvas(parent, wx.ID_ANY, style = wx.VSCROLL)
	panel.SetScrollbars(1, 40, 1, 40)
	GUI_ELEMENTS['notifications_panel'] = panel
	return panel

def create_notifications_header_text(parent):
	global GUI_ELEMENTS
	global NOTIFICATION_ENTRIES
	num_notifications = len(NOTIFICATION_ENTRIES)
	displayed = str(num_notifications) + ' notifications found.'
	text = wx.TextCtrl(parent, wx.ID_ANY, displayed, style = wx.BORDER_NONE|wx.TE_READONLY)
	GUI_ELEMENTS['notifications_header_text'] = text
	return text

def create_notification_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_notification_horizontal_sizer():
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	return sizer

def create_notification_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_notification_sub_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def notification_remove_notification_button_callback_generator(panel, entry):
	def callback(arg):
		global GUI_ELEMENTS
		global NOTIFICATION_ENTRIES
		panel.Destroy()
		NOTIFICATION_ENTRIES.remove(entry)
		num_notifications = len(NOTIFICATION_ENTRIES)
		displayed = str(num_notifications) + ' notifications found.'
		GUI_ELEMENTS['notifications_header_text'].SetValue(displayed)
		GUI_ELEMENTS['main_frame'].Layout()
	return callback

def create_notification_remove_notification_button(parent, panel, entry):
	button = wx.Button(parent, wx.ID_ANY, "Remove Notification")
	callback = notification_remove_notification_button_callback_generator(panel, entry)
	button.Bind(wx.EVT_BUTTON, callback)
	return button

def create_notification_newad_front_text(parent, text):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	text = wx.TextCtrl(parent, wx.ID_ANY, text, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL|wx.TE_RICH)
	text.SetBackgroundColour(wx.Colour(240,240,240))
	text.SetStyle(0, 500, attr)
	return text

def create_notification_newad_title(parent, title):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	text = wx.TextCtrl(parent, wx.ID_ANY, title, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL|wx.TE_RICH)
	text.SetBackgroundColour(wx.Colour(240, 240, 240))
	text.SetStyle(0, 500, attr)
	return text

def create_notification_newad_price(parent, price):
	text = wx.TextCtrl(parent, wx.ID_ANY, price, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL)
	text.SetBackgroundColour(wx.Colour(240, 240, 240))
	return text

def create_notification_newad_adtitle(parent, title):
	text = wx.TextCtrl(parent, wx.ID_ANY, title, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL)
	text.SetBackgroundColour(wx.Colour(240, 240, 240))
	return text

def create_notification_newad_url(parent, url):
	text = wx.TextCtrl(parent, wx.ID_ANY, url, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL)
	text.SetBackgroundColour(wx.Colour(240, 240, 240))
	return text

def generate_notification_newad(parent, notification_dict):
	front_text = notification_dict.get('front_text')
	notification_title = notification_dict.get('notification_title')
	ad_price = convert_price_to_display(notification_dict.get('ad_price'))
	ad_title = notification_dict.get('ad_title')
	ad_url = notification_dict.get('ad_url')
	# creating panels and setting sizers
	notification_panel = create_notification_panel(parent)
	notification_panel_sizer = create_notification_panel_sizer()
	notification_panel.SetSizer(notification_panel_sizer)
	subpanel_1 = create_notification_sub_panel(notification_panel)
	subpanel_2 = create_notification_sub_panel(notification_panel)
	subpanel_3 = create_notification_sub_panel(notification_panel)
	subpanel_4 = create_notification_sub_panel(notification_panel)
	horiz_sizer_1 = create_notification_horizontal_sizer()
	horiz_sizer_2 = create_notification_horizontal_sizer()
	horiz_sizer_3 = create_notification_horizontal_sizer()
	horiz_sizer_4 = create_notification_horizontal_sizer()
	subpanel_1.SetSizer(horiz_sizer_1)
	subpanel_2.SetSizer(horiz_sizer_2)
	subpanel_3.SetSizer(horiz_sizer_3)
	subpanel_4.SetSizer(horiz_sizer_4)
	# creating elements
	newad_front_text = create_notification_newad_front_text(subpanel_1, front_text)
	newad_notification_title = create_notification_newad_title(subpanel_1, notification_title)
	newad_ad_price = create_notification_newad_price(subpanel_2, ad_price)
	newad_ad_title = create_notification_newad_adtitle(subpanel_2, ad_title)
	newad_ad_url = create_notification_newad_url(subpanel_3, ad_url)
	remove_notification_button = create_notification_remove_notification_button(subpanel_4, notification_panel, notification_dict)
	# putting in sizers
	horiz_sizer_1.Add(newad_front_text, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_1.Add(newad_notification_title, 5, wx.ALL|wx.EXPAND)
	horiz_sizer_2.Add(newad_ad_price, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_2.Add(newad_ad_title, 5, wx.ALL|wx.EXPAND)
	horiz_sizer_3.Add(newad_ad_url, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_4.Add(remove_notification_button, 0, wx.ALL|wx.EXPAND)
	notification_panel_sizer.Add(subpanel_1, 0, wx.ALL|wx.EXPAND, 5)
	notification_panel_sizer.Add(subpanel_2, 0, wx.ALL|wx.EXPAND, 5)
	notification_panel_sizer.Add(subpanel_3, 0, wx.ALL|wx.EXPAND, 5)
	notification_panel_sizer.Add(subpanel_4, 0, wx.ALL|wx.EXPAND, 5)
	return notification_panel

def generate_notification(parent, notification_dict):
	notification_type = notification_dict.get('notification_type')
	if notification_type == 'newad':
		return generate_notification_newad(parent, notification_dict)

def generate_notifications_view(parent):
	global GUI_ELEMENTS
	global NOTIFICATION_ENTRIES
	notifications_view_sizer = create_notifications_view_sizer()
	notifications_view_panel = create_notifications_view_panel(parent)
	notifications_view_panel.SetSizer(notifications_view_sizer)
	notifications_panel_sizer = create_notifications_panel_sizer()
	notifications_panel = create_notifications_panel(notifications_view_panel)
	notifications_panel.SetSizer(notifications_panel_sizer)
	notifications_header = create_notifications_header_text(notifications_view_panel)
	notifications_view_sizer.Add(notifications_header, 0, wx.ALL|wx.EXPAND, 5)
	notifications_view_sizer.Add(notifications_panel, 1, wx.ALL|wx.EXPAND, 5)
	for entry in NOTIFICATION_ENTRIES:
		notification_panel = generate_notification(notifications_panel, entry)
		notifications_panel_sizer.Prepend(notification_panel, 0, wx.ALL|wx.EXPAND, 5)
	return notifications_view_panel

def destroy_notifications_view():
	global GUI_ELEMENTS
	GUI_ELEMENTS['notifications_view_panel'].Destroy()

def update_notifications_view():
	global GUI_ELEMENTS
	main_frame = GUI_ELEMENTS['main_frame']
	main_frame_sizer = GUI_ELEMENTS['main_frame_sizer']
	destroy_notifications_view()
	notifications_view = generate_notifications_view(main_frame)
	main_frame_sizer.Add(notifications_view, 1, wx.ALL|wx.EXPAND)
	main_frame.Layout()

def show_notifications_view():
	global GUI_ELEMENTS
	GUI_ELEMENTS['notifications_view_panel'].Show()

def hide_notifications_view():
	global GUI_ELEMENTS
	GUI_ELEMENTS['notifications_view_panel'].Hide()


"""-----------------------------------------------------------------------------

	Trackers View creation

-----------------------------------------------------------------------------"""

def create_trackers_view_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_trackers_view_panel(parent):
	global GUI_ELEMENTS
	panel = wx.Panel(parent, wx.ID_ANY)
	GUI_ELEMENTS['trackers_view_panel'] = panel
	return panel

def create_trackers_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_trackers_panel(parent):
	global GUI_ELEMENTS
	panel = wx.ScrolledCanvas(parent, wx.ID_ANY, style = wx.VSCROLL)
	panel.SetScrollbars(1, 40, 1, 40)
	GUI_ELEMENTS['trackers_panel'] = panel
	return panel

def create_trackers_header_text(parent):
	global TRACKER_ENTRIES
	num_trackers = len(TRACKER_ENTRIES)
	displayed = str(num_trackers) + ' running trackers found.'
	text = wx.TextCtrl(parent, wx.ID_ANY, displayed, style = wx.BORDER_NONE|wx.TE_READONLY)
	return text

def generate_trackers_view(parent):
	global TRACKER_ENTRIES
	trackers_view_sizer = create_trackers_view_sizer()
	trackers_view_panel = create_trackers_view_panel(parent)
	trackers_view_panel.SetSizer(trackers_view_sizer)
	trackers_panel_sizer = create_trackers_panel_sizer()
	trackers_panel = create_trackers_panel(trackers_view_panel)
	trackers_panel.SetSizer(trackers_panel_sizer)
	trackers_header = create_trackers_header_text(trackers_view_panel)
	trackers_view_sizer.Add(trackers_header, 0, wx.ALL|wx.EXPAND, 5)
	trackers_view_sizer.Add(trackers_panel, 1, wx.ALL|wx.EXPAND, 5)
	return trackers_view_panel

def destroy_trackers_view():
	global GUI_ELEMENTS
	GUI_ELEMENTS['trackers_view_panel'].Destroy()

def show_trackers_view():
	global GUI_ELEMENTS
	GUI_ELEMENTS['trackers_view_panel'].Show()

def hide_trackers_view():
	global GUI_ELEMENTS
	GUI_ELEMENTS['trackers_view_panel'].Hide()


"""-----------------------------------------------------------------------------

	Main Frame creation
	
-----------------------------------------------------------------------------"""

def create_main_frame():
	frame = wx.Frame(None, wx.ID_ANY, "Kijiji Scraper")
	frame.Show()
	frame.Centre()
	frame.Maximize()
	return frame

def create_main_frame_sizer():
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	return sizer

def generate_main_frame():
	global GUI_ELEMENTS
	main_frame = create_main_frame()
	options_panel = generate_options_panel(main_frame)
	sizer = create_main_frame_sizer()
	sizer.Add(options_panel, 0, wx.ALL|wx.EXPAND)
	main_frame.SetSizer(sizer)
	GUI_ELEMENTS['main_frame'] = main_frame
	GUI_ELEMENTS['main_frame_sizer'] = sizer
	return main_frame


"""-----------------------------------------------------------------------------

	State changes
	
-----------------------------------------------------------------------------"""

def instantiate_all_views():
	global GUI_ELEMENTS
	main_frame = GUI_ELEMENTS['main_frame']
	main_frame_sizer = GUI_ELEMENTS['main_frame_sizer']
	scrape_view = generate_scrape_view(main_frame)
	notifications_view = generate_notifications_view(main_frame)
	trackers_view = generate_trackers_view(main_frame)
	main_frame_sizer.Add(scrape_view, 1, wx.ALL|wx.EXPAND)
	main_frame_sizer.Add(notifications_view, 1, wx.ALL|wx.EXPAND)
	main_frame_sizer.Add(trackers_view, 1, wx.ALL|wx.EXPAND)

def hide_all_views():
	hide_scrape_view()
	hide_notifications_view()
	hide_trackers_view()

def change_view(new_view):
	global GUI_ELEMENTS
	global ACTIVE_VIEW
	if new_view != ACTIVE_VIEW:
		if ACTIVE_VIEW == 'scraping':
			hide_scrape_view()
		elif ACTIVE_VIEW == 'notifications':
			hide_notifications_view()
		elif ACTIVE_VIEW == 'trackers':
			hide_trackers_view()
		# create new view and display relevant options
		main_frame = GUI_ELEMENTS['main_frame']
		main_frame_sizer = GUI_ELEMENTS['main_frame_sizer']
		change_options_panel_state(new_view)
		if new_view == 'scraping':
			show_scrape_view()
			ACTIVE_VIEW = 'scraping'
		elif new_view == 'notifications':
			show_notifications_view()
			ACTIVE_VIEW = 'notifications'
		elif new_view == 'trackers':
			show_trackers_view()
			ACTIVE_VIEW	 = 'trackers'
		main_frame.Layout()


def main():
	app = create_app()
	main_frame = generate_main_frame()
	instantiate_all_views()
	hide_all_views()
	change_view('scraping')
	# def otherloop():
	# 	while True:
	# 		print('hello')
	# 		time.sleep(1)
	# thread = threading.Thread(None, otherloop)
	# thread.start()
	app.MainLoop()

if __name__ == "__main__":
	main()
	