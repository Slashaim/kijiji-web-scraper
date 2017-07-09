"""-----------------------------------------------------------------------------

	scraping.py

	Used to control scraping UI and state.

-----------------------------------------------------------------------------"""

import wx
import asyncio
import time

import lib.kijiji_scraper
import lib.helpers
import lib.client_state


"""-----------------------------------------------------------------------------

	Globals
	
-----------------------------------------------------------------------------"""

global USER_PRODUCT_NAME
global USER_LOCATION_INDEX
global USER_MAX_ADS
global USER_MAX_PRICE
USER_PRODUCT_NAME = None
USER_LOCATION_INDEX = None
USER_MAX_ADS = None
USER_MAX_PRICE = None


"""-----------------------------------------------------------------------------

	Scrape Options creation
	
-----------------------------------------------------------------------------"""

def create_scrape_options_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_scrape_options_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	lib.client_state.gui_elements['scrape_options_panel'] = panel
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
	global USER_PRODUCT_NAME
	startingText = USER_PRODUCT_NAME or ''
	text_box = wx.TextCtrl(parent, wx.ID_ANY, startingText)
	lib.client_state.gui_elements['product_name_text_box'] = text_box
	return text_box

def create_only_new_checkbox(parent):
	checkbox = wx.CheckBox(parent, wx.ID_ANY, "Only scrape new ads")
	lib.client_state.gui_elements['only_new_checkbox'] = checkbox
	return checkbox

def create_max_ads_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Max Ads Shown:", style = wx.TE_READONLY|wx.TE_RIGHT|wx.BORDER_NONE)
	return label

def create_max_ads_text_box(parent):
	startingText = str(USER_MAX_ADS or lib.client_state.max_ads)
	textbox = wx.TextCtrl(parent, wx.ID_ANY, startingText)
	lib.client_state.gui_elements['max_ads_text_box'] = textbox
	return textbox

def create_max_price_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Display if below price:", style = wx.TE_READONLY|wx.TE_RIGHT|wx.BORDER_NONE)
	return label

def create_max_price_text_box(parent):
	textbox = wx.TextCtrl(parent, wx.ID_ANY, '')
	lib.client_state.gui_elements['max_price_text_box'] = textbox
	return textbox

def create_show_top_ads_checkbox(parent):
	checkbox = wx.CheckBox(parent, wx.ID_ANY, "Show Top Ads")
	lib.client_state.gui_elements['show_top_ads_checkbox'] = checkbox
	return checkbox

def create_show_third_party_ads_checkbox(parent):
	checkbox = wx.CheckBox(parent, wx.ID_ANY, "Show Third-Party Ads")
	lib.client_state.gui_elements['show_third_party_ads_checkbox'] = checkbox
	return checkbox

def create_location_choice(parent):
	global USER_LOCATION_INDEX
	startingChoice = USER_LOCATION_INDEX or 0
	choice = wx.Choice(parent, wx.ID_ANY, choices = lib.client_state.valid_locations)
	choice.SetSelection(startingChoice)
	lib.client_state.gui_elements['location_choice'] = choice
	return choice

def scrape_button_callback(arg):
	global USER_PRODUCT_NAME
	global USER_MAX_ADS
	global USER_LOCATION_INDEX
	global USER_MAX_PRICE
	product_name_text_box = lib.client_state.gui_elements['product_name_text_box']
	location_choice = lib.client_state.gui_elements['location_choice']
	scrape_message = lib.client_state.gui_elements['scrape_message']
	max_ads_text_box = lib.client_state.gui_elements['max_ads_text_box']
	max_price_text_box = lib.client_state.gui_elements['max_price_text_box']
	only_new_checkbox = lib.client_state.gui_elements['only_new_checkbox']
	show_top_ads_checkbox = lib.client_state.gui_elements['show_top_ads_checkbox']
	show_third_party_ads_checkbox = lib.client_state.gui_elements['show_third_party_ads_checkbox']
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
	given_max_ads = lib.helpers.get_max_ads(max_ads_text_box.GetLineText(lineNo = 0))
	given_max_price = lib.helpers.get_max_price(max_price_text_box.GetLineText(lineNo = 0))
	given_location = location_choice.GetSelection()
	location = lib.client_state.ui_to_location.get(location_choice.GetString(given_location))
	if not lib.helpers.valid_product_name(given_product_name):
		scrape_message.SetValue('Invalid product name. Only alphabetical and numeric characters are supported.')
		product_name_text_box.SetBackgroundColour(wx.Colour(255, 240, 240))
		product_name_text_box.Refresh()
		return
	if not given_max_ads or not 1 <= given_max_ads <= lib.client_state.max_ads:
		max_ads_text_box.SetBackgroundColour(wx.Colour(255, 240, 240))
		max_ads_text_box.Refresh()
		scrape_message.SetValue('Invalid maximum ad number. Must be between 1 and ' + str(lib.client_state.max_ads) + '.')
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
	# updating ad entries
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

	def entry_break(ad):
		is_normal_ad = ad['html_class'] == 'normal'
		has_been_seen = ad['ad_id'] in lib.client_state.viewed_ad_ids
		return only_new_ads and is_normal_ad and has_been_seen

	def post_proc(ad_list):
		if only_new_ads:
			last_index = 0
			for index, ad in enumerate(ad_list):
				if ad['ad_id'] in lib.client_state.viewed_ad_ids:
					last_index = index
					break
			last_index = min(last_index, given_max_ads)
			return ad_list[:last_index]
		else:
			return ad_list[:given_max_ads]

	try:
		start_time = time.perf_counter()
		lib.client_state.ad_entries = lib.kijiji_scraper.get_ad_entries_from_constraints(
			parameters = {
				'product_name': given_product_name,
				'location': location,
				'only_new_ads': only_new_ads,
				'entry_incl': entry_incl,
				'entry_break': entry_break,
				'post_proc': post_proc		
			},
			list_check = list_check
		)
		print(str(time.perf_counter() - start_time))
		for ad in lib.client_state.ad_entries:
			ad['location'] = lib.client_state.location_to_ui.get(ad['location'])
			lib.client_state.viewed_ad_ids.add(ad['ad_id'])
		start_time = time.perf_counter()
		update_scrape_view()
		print(str(time.perf_counter() - start_time))
	except asyncio.TimeoutError:
		scrape_message.SetValue('Connection timed out. Check internet connectivity or try again later.')

def create_scrape_button(parent):
	button = wx.Button(parent, wx.ID_ANY, "Scrape")
	button.Bind(wx.EVT_BUTTON, scrape_button_callback)
	lib.client_state.gui_elements['scrape_button'] = button
	return button

def create_scrape_message(parent):
	label = wx.TextCtrl(parent, wx.ID_ANY, "", style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
	label.SetBackgroundColour(wx.Colour(240,240,240))
	lib.client_state.gui_elements['scrape_message'] = label
	return label

def generate_scrape_options(parent):
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
	lib.client_state.gui_elements['scrape_options_panel'] = scrape_options_panel
	return scrape_options_panel

def show_scrape_options():
	lib.client_state.gui_elements['scrape_options_panel'].Show()

def hide_scrape_options():
	lib.client_state.gui_elements['scrape_options_panel'].Hide()

"""-----------------------------------------------------------------------------

	Scrape View creation

-----------------------------------------------------------------------------"""

def create_scrape_view_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_scrape_view_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	lib.client_state.gui_elements['scrape_view_panel'] = panel
	return panel

def create_ads_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_ads_panel(parent):
	panel = wx.ScrolledCanvas(parent, wx.ID_ANY, style = wx.VSCROLL)
	panel.SetScrollbars(1, 40, 1, 40)
	lib.client_state.gui_elements['ads_panel'] = panel
	return panel

def create_ad_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_ad_horizontal_sizer():
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	return sizer

def create_scrape_header_text(parent):
	num_ads = len(lib.client_state.ad_entries)
	displayed = 'No ads found.'
	if num_ads == 1:
		displayed = str(num_ads) + ' ad found.'
	elif num_ads > 1:
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
	price = lib.helpers.convert_price_to_display(ad_dict.get('price'))
	date_posted = ad_dict.get('date_posted')
	location = ad_dict.get('location')
	url = ad_dict.get('url')
	description = ad_dict.get('description')
	html_class = lib.helpers.convert_html_class_to_display(ad_dict.get('html_class'))
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
	scrape_view_sizer = create_scrape_view_sizer()
	scrape_view_panel = create_scrape_view_panel(parent)
	scrape_view_panel.SetSizer(scrape_view_sizer)
	ads_panel_sizer = create_ads_panel_sizer()
	ads_panel = create_ads_panel(scrape_view_panel)
	ads_panel.SetSizer(ads_panel_sizer)
	scrape_header_text = create_scrape_header_text(scrape_view_panel)
	scrape_view_sizer.Add(scrape_header_text, 0, wx.ALL|wx.EXPAND, 5)
	scrape_view_sizer.Add(ads_panel, 1, wx.ALL|wx.EXPAND, 5)
	for ad in lib.client_state.ad_entries:
		ad_panel = generate_ad_panel(ads_panel, ad)
		ads_panel_sizer.Add(ad_panel, 0, wx.ALL|wx.EXPAND, 5)
	return scrape_view_panel

def destroy_scrape_view():
	lib.client_state.gui_elements['scrape_view_panel'].Destroy()

def update_scrape_view():
	main_frame = lib.client_state.gui_elements['main_frame']
	main_frame_sizer = lib.client_state.gui_elements['main_frame_sizer']
	destroy_scrape_view()
	scrape_view = generate_scrape_view(main_frame)
	main_frame_sizer.Add(scrape_view, 1, wx.ALL|wx.EXPAND)
	main_frame.Layout()

def show_scrape_view():
	lib.client_state.gui_elements['scrape_view_panel'].Show()

def hide_scrape_view():
	lib.client_state.gui_elements['scrape_view_panel'].Hide()