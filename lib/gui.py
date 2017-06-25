"""-----------------------------------------------------------------------------

	gui.py

	Controls the creation of the GUI.
	
-----------------------------------------------------------------------------"""

import wx
import re
import asyncio
import kijiji_scraper


"""-----------------------------------------------------------------------------

	Globals
	
-----------------------------------------------------------------------------"""

global GUI_ELEMENTS
global VALID_LOCATIONS
global AD_ENTRIES
global ACTIVE_VIEW
global UI_TO_LOCATION
global HARD_MAX_AD_NUMBER

GUI_ELEMENTS = {}
VALID_LOCATIONS = [
	'All of Toronto (GTA)',
	'City of Toronto'
]
AD_ENTRIES = []
ACTIVE_VIEW = None
UI_TO_LOCATION = {
	'All of Toronto (GTA)': 'all-of-toronto',
	'City of Toronto': 'city-of-toronto'
}
HARD_MAX_AD_NUMBER = 50

global DUMMY
DUMMY = {
	'title': 'Test',
	'price': 500.00,
	'description': 'Foo',
	'location': 'Here',
	'date_posted': '5 seconds ago',
	'url': 'http://website.org'
}
global OTHER_DUMMY
OTHER_DUMMY = {
	'title': 'Example',
	'price': 'this is the price',
	'description': 'Bar',
	'location': 'Not here',
	'date_posted': '5 years ago',
	'url': 'http://website.org'
}
AD_ENTRIES.append(DUMMY)
AD_ENTRIES.append(OTHER_DUMMY)
for i in range(0, 30):
	AD_ENTRIES.append(DUMMY)

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

def threads_mode_button_callback(arg):
	change_view('threads')

def create_threads_mode_button(parent):
	button = wx.Button(parent, wx.ID_ANY, "Threads View")
	button.Bind(wx.EVT_BUTTON, threads_mode_button_callback)
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
	threads_mode_button = create_threads_mode_button(views_panel)
	# adding to sizer
	views_sizer.Add(views_label, 0, wx.ALL|wx.EXPAND)
	views_sizer.Add(scrape_mode_button, 0, wx.ALL|wx.EXPAND, 5)
	views_sizer.Add(notifications_mode_button, 0, wx.ALL|wx.EXPAND, 5)
	views_sizer.Add(threads_mode_button, 0, wx.ALL|wx.EXPAND, 5)
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

def only_new_checkbox_callback(arg):
	print("Checkbox event fired")

def create_only_new_checkbox(parent):
	checkbox = wx.CheckBox(parent, wx.ID_ANY, "Only scrape new ads")
	checkbox.Bind(wx.EVT_CHECKBOX, only_new_checkbox_callback)
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
	given_product_name = product_name_text_box.GetLineText(lineNo = 0)
	given_max_ads = get_max_ads(max_ads_text_box.GetLineText(lineNo = 0))
	given_max_price = get_max_price(max_price_text_box.GetLineText(lineNo = 0))
	given_location = location_choice.GetSelection()
	location = UI_TO_LOCATION.get(location_choice.GetString(given_location))
	# checking for valid inputs
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
	# creating parts
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
	print("Clear all notifications button pressed")

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

	Threads Options creation
	
-----------------------------------------------------------------------------"""

def create_threads_options_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_threads_options_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_threads_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Threads", style = wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_NONE)
	return label

def send_all_notifications_callback(arg):
	print("Send all notifications button pressed")

def create_send_all_notifications_button(parent):
	global GUI_ELEMENTS
	button = wx.Button(parent, wx.ID_ANY, "Send All Tray Notifications")
	button.Bind(wx.EVT_BUTTON, send_all_notifications_callback)
	GUI_ELEMENTS['send_all_notifications_button'] = button
	return button

def stop_all_notifications_callback(parent):
	print("Stop all notifications button pressed")

def create_stop_all_notifications_button(parent):
	global GUI_ELEMENTS
	button = wx.Button(parent, wx.ID_ANY, "Stop All Tray Notifications")
	button.Bind(wx.EVT_BUTTON, stop_all_notifications_callback)
	GUI_ELEMENTS['stop_all_notifications_button'] = button
	return button 

def kill_all_threads_button_callback(arg):
	print("Kill all threads button pressed")

def create_kill_all_threads_button(parent):
	global GUI_ELEMENTS
	button = wx.Button(parent, wx.ID_ANY, "Kill All Threads")
	button.Bind(wx.EVT_BUTTON, kill_all_threads_button_callback)
	GUI_ELEMENTS['kill_all_threads_button'] = button
	return button

def generate_threads_options(parent):
	global GUI_ELEMENTS
	# creating panel and setting sizer
	threads_options_panel = create_threads_options_panel(parent)
	threads_options_sizer = create_threads_options_sizer()
	threads_options_panel.SetSizer(threads_options_sizer)
	# creating elements
	threads_label = create_threads_label(threads_options_panel)
	send_all_notifications_button = create_send_all_notifications_button(threads_options_panel)
	stop_all_notifications_button = create_stop_all_notifications_button(threads_options_panel)
	kill_all_threads_button = create_kill_all_threads_button(threads_options_panel)
	# putting in sizers
	threads_options_sizer.Add(threads_label, 0, wx.ALL|wx.EXPAND)
	threads_options_sizer.Add(send_all_notifications_button, 0, wx.ALL|wx.EXPAND, 5)
	threads_options_sizer.Add(stop_all_notifications_button, 0, wx.ALL|wx.EXPAND, 5)
	threads_options_sizer.Add(kill_all_threads_button, 0, wx.ALL|wx.EXPAND, 5)
	GUI_ELEMENTS['threads_options_panel'] = threads_options_panel
	return threads_options_panel


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
	elif new_view == 'threads':
		threads_options = generate_threads_options(options_panel)
		options_sizer.Add(threads_options, 0, wx.ALL|wx.EXPAND)


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

def generate_notifications_view(parent):
	pass

def destroy_notifications_view():
	pass


"""-----------------------------------------------------------------------------

	Threads View creation

-----------------------------------------------------------------------------"""

def create_threads_view_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_threads_view_panel(parent):
	global GUI_ELEMENTS
	panel = wx.Panel(parent, wx.ID_ANY)
	GUI_ELEMENTS['threads_view_panel'] = panel
	return panel

def generate_threads_view(parent):
	pass

def destroy_threads_view():
	pass

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

def change_view(new_view):
	global ACTIVE_VIEW
	if new_view != ACTIVE_VIEW:
		if ACTIVE_VIEW == 'scraping':
			destroy_scrape_view()
		elif ACTIVE_VIEW == 'notifications':
			destroy_notifications_view()
		elif ACTIVE_VIEW == 'threads':
			destroy_threads_view()
		# create new view and display relevant options
		main_frame = GUI_ELEMENTS['main_frame']
		main_frame_sizer = GUI_ELEMENTS['main_frame_sizer']
		change_options_panel_state(new_view)
		if new_view == 'scraping':
			scrape_view = generate_scrape_view(main_frame)
			ads_panel = GUI_ELEMENTS['ads_panel']
			main_frame_sizer.Add(scrape_view, 1, wx.ALL|wx.EXPAND)
			ACTIVE_VIEW = 'scraping'
		elif new_view == 'notifications':
			notifications_view = generate_notifications_view(main_frame)
			# main_frame_sizer.Add(notifications_view, 1, wx.ALL|wx.EXPAND)
			ACTIVE_VIEW = 'notifications'
		elif new_view == 'threads':
			threads_view = generate_threads_view(main_frame)
			# main_frame_sizer.Add(threads_view, 1, wx.ALL|wx.EXPAND)
			ACTIVE_VIEW	 = 'threads'
		main_frame.Layout()


def main():
	app = create_app()
	main_frame = generate_main_frame()
	change_view('scraping')
	app.MainLoop()


if __name__ == "__main__":
	main()
	