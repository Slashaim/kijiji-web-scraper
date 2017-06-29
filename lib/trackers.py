"""-----------------------------------------------------------------------------

	trackers.py

	Used to control trackers UI and state.

-----------------------------------------------------------------------------"""

import wx
import re
import time
import datetime
import asyncio
import threading

import kijiji_scraper
import helpers
import client_state

global USER_SHOW_TRAY_NOTIFICATIONS
USER_SHOW_TRAY_NOTIFICATIONS = False


"""-----------------------------------------------------------------------------

	Trackers Options creation
	
-----------------------------------------------------------------------------"""

def create_trackers_options_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_trackers_options_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	client_state.gui_elements['trackers_options_panel'] = panel
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
	text_box = wx.TextCtrl(parent, wx.ID_ANY)
	client_state.gui_elements['tracker_product_name_text_box'] = text_box
	return text_box

def create_tracker_max_price_text_box_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Max Price:", style = wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_NONE)
	return label

def create_tracker_max_price_text_box(parent):
	text_box = wx.TextCtrl(parent, wx.ID_ANY)
	client_state.gui_elements['tracker_max_price_text_box'] = text_box
	return text_box

def create_tracker_location_choice(parent):
	choice = wx.Choice(parent, wx.ID_ANY, choices = client_state.valid_locations)
	choice.SetSelection(0)
	client_state.gui_elements['tracker_location_choice'] = choice
	return choice

def tracker_button_callback(arg):
	tracker_product_name_text_box = client_state.gui_elements['tracker_product_name_text_box']
	tracker_max_price_text_box = client_state.gui_elements['tracker_max_price_text_box']
	tracker_location_choice = client_state.gui_elements['tracker_location_choice']
	tracker_message = client_state.gui_elements['tracker_message']
	# setting initial gui state
	tracker_product_name_text_box.SetBackgroundColour(wx.Colour(255, 255, 255))
	tracker_product_name_text_box.Refresh()
	tracker_message.SetValue('')
	# getting initial gui state and checking for valid inputs
	given_product_name = tracker_product_name_text_box.GetLineText(lineNo = 0)
	given_max_price = helpers.get_max_price(max_price_text_box.GetLineText(lineNo = 0))
	given_location = tracker_location_choice.GetSelection()
	location = client_state.ui_to_location.get(location_choice.GetString(given_location))
	if not helpers.valid_product_name(given_product_name):
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
	button = wx.Button(parent, wx.ID_ANY, "Create New Tracker")
	button.Bind(wx.EVT_BUTTON, tracker_button_callback)
	client_state.gui_elements['tracker_button'] = button
	return button

def show_tray_notifications_checkbox_callback(arg):
	global USER_SHOW_TRAY_NOTIFICATIONS
	USER_SHOW_TRAY_NOTIFICATIONS = arg.IsChecked()

def create_show_tray_notifications_checkbox(parent):
	checkbox = wx.CheckBox(parent, wx.ID_ANY, "Show Tray Notifications")
	checkbox.Bind(wx.EVT_CHECKBOX, show_tray_notifications_checkbox_callback)
	client_state.gui_elements['show_tray_notifications'] = checkbox
	return checkbox

def create_tracker_message(parent):
	label = wx.TextCtrl(parent, wx.ID_ANY, "", style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
	label.SetBackgroundColour(wx.Colour(240,240,240))
	client_state.gui_elements['tracker_message'] = label
	return label

def generate_trackers_options(parent):
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
	return trackers_options_panel


"""-----------------------------------------------------------------------------

	Trackers Options actions
	
-----------------------------------------------------------------------------"""

def add_tracker_entry(tracker_dict):
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
	client_state.tracker_entries.append(entry)

def time_update_tracker_entry(entry):
	current_time = time.perf_counter()
	start_time = entry['start_time']
	last_scrape_time = entry['last_scrape_time']
	cycle_time = entry['cycle_time']
	entry['active_time'] = current_time - start_time
	entry['time_to_next_scrape'] = (last_scrape_time + cycle_time) - current_time
	if (current_time - last_scrape_time) > cycle_time:
		entry['scrape_on_next'] = True

def gui_update_tracker_entry(entry):
	clamped_active_time = helpers.clamp(entry['active_time'], minimum = 0)
	formatted_active_time = str(datetime.timedelta(seconds = round(clamped_active_time)))
	entry['gui_active_time'].SetValue(formatted_active_time)
	clamped_time_to_next_scrape = helpers.clamp(entry['time_to_next_scrape'], minimum = 0)
	formatted_time_to_next_scrape = str(datetime.timedelta(seconds = round(clamped_time_to_next_scrape)))
	entry['gui_scrape_time'].SetValue(formatted_time_to_next_scrape)

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
		if max_price:
			try:
				price_allowed = price <= max_price
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
	product_name = entry['product_name']
	location = client_state.location_to_ui[entry['location']]
	viewed_ads = entry['viewed_ads']
	given_max_price = entry.get('max_price')
	max_price = helpers.convert_price_to_display(entry.get('max_price'))
	scrape_on_next = entry['scrape_on_next']
	if scrape_on_next:
		ads = get_new_ads_for_notifications(entry)
		for ad in ads:
			viewed_ads.add(ad)
			notification_title = get_notification_title_from_newad(ad)
			ad_price = helpers.convert_price_to_display(ad.get('price'))
			ad_title = ad.get('title')
			ad_url = ad.get('url')
			client_state.notification_entries.append({
				'notification_type': 'newad',
				'front_text': 'New Ad',
				'notification_title': notification_title,
				'ad_price': ad_price,
				'ad_title': ad_title,
				'ad_url': ad_url
			})
		if len(ads) > 0: 
			if USER_SHOW_TRAY_NOTIFICATIONS:
				pass
			if client_state.active_view == 'notifications':
				pass

def create_tracker_time_update_thread():
	def time_update_loop():
		while client_state.app_open:
			for entry in client_state.tracker_entries:
				time_update_tracker_entry(entry)
				gui_update_tracker_entry(entry)
			time.sleep(0.8)
	thread = threading.Thread(None, target = time_update_loop)
	thread.start()



"""-----------------------------------------------------------------------------

	Trackers View creation

-----------------------------------------------------------------------------"""

def create_trackers_view_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_trackers_view_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	client_state.gui_elements['trackers_view_panel'] = panel
	return panel

def create_trackers_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_trackers_panel(parent):
	panel = wx.ScrolledCanvas(parent, wx.ID_ANY, style = wx.VSCROLL)
	panel.SetScrollbars(1, 40, 1, 40)
	client_state.gui_elements['trackers_panel'] = panel
	return panel

def create_trackers_header_text(parent):
	num_trackers = len(client_state.tracker_entries)
	displayed = str(num_trackers) + ' running trackers found.'
	text = wx.TextCtrl(parent, wx.ID_ANY, displayed, style = wx.BORDER_NONE|wx.TE_READONLY)
	client_state.gui_elements['trackers_header_text'] = text
	return text

def create_tracker_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_tracker_horizontal_sizer():
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	return sizer

def create_tracker_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_tracker_sub_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	return panel

def create_tracker_product_name(parent, name):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	text = wx.TextCtrl(parent, wx.ID_ANY, name, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL|wx.TE_RICH)
	text.SetBackgroundColour(wx.Colour(240,240,240))
	text.SetStyle(0, 500, attr)
	return text

def create_tracker_location(parent, location):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	text = wx.TextCtrl(parent, wx.ID_ANY, location, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL|wx.TE_RICH)
	text.SetBackgroundColour(wx.Colour(240,240,240))
	text.SetStyle(0, 500, attr)
	return text

def create_tracker_max_price(parent, max_price):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	text = wx.TextCtrl(parent, wx.ID_ANY, max_price, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL|wx.TE_RICH)
	text.SetBackgroundColour(wx.Colour(240,240,240))
	text.SetStyle(0, 500, attr)
	return text

def create_tracker_active_time_label(parent):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	text = wx.TextCtrl(parent, wx.ID_ANY, "Active Time:", style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL|wx.TE_RICH)
	text.SetBackgroundColour(wx.Colour(240,240,240))
	text.SetStyle(0, 500, attr)
	return text

def create_tracker_active_time(parent, ad_entry):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	text = wx.TextCtrl(parent, wx.ID_ANY, "", style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL|wx.TE_RICH)
	text.SetBackgroundColour(wx.Colour(240,240,240))
	text.SetStyle(0, 500, attr)
	ad_entry['gui_active_time'] = text
	return text

def create_tracker_scrape_time_label(parent):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	text = wx.TextCtrl(parent, wx.ID_ANY, "Time to next scrape:", style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL|wx.TE_RICH)
	text.SetBackgroundColour(wx.Colour(240,240,240))
	text.SetStyle(0, 500, attr)
	return text

def create_tracker_scrape_time(parent, ad_entry):
	attr = wx.TextAttr()
	attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
	text = wx.TextCtrl(parent, wx.ID_ANY, "", style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL|wx.TE_RICH)
	text.SetBackgroundColour(wx.Colour(240,240,240))
	text.SetStyle(0, 500, attr)
	ad_entry['gui_scrape_time'] = text
	return text

def tracker_remove_tracker_button_callback_generator(panel, entry):
	def callback(arg):
		panel.Destroy()
		client_state.tracker_entries.remove(entry)
		num_trackers = len(client_state.tracker_entries)
		displayed = str(num_trackers) + ' running trackers found.'
		client_state.gui_elements['trackers_header_text'].SetValue(displayed)
		client_state.gui_elements['main_frame'].Layout()
	return callback

def create_remove_tracker_button(parent, panel, entry):
	button = wx.Button(parent, wx.ID_ANY, "Remove Tracker")
	callback = tracker_remove_tracker_button_callback_generator(panel, entry)
	button.Bind(wx.EVT_BUTTON, callback)
	return button

def generate_tracker(parent, tracker_dict):
	product_name = tracker_dict.get('product_name')
	location = client_state.location_to_ui[tracker_dict['location']]
	max_price = helpers.convert_price_to_display(tracker_dict.get('max_price'))
	# creating panels and setting sizers
	tracker_panel = create_tracker_panel(parent)
	tracker_panel_sizer = create_tracker_panel_sizer()
	tracker_panel.SetSizer(tracker_panel_sizer)
	subpanel_1 = create_tracker_sub_panel(tracker_panel)
	subpanel_2 = create_tracker_sub_panel(tracker_panel)
	subpanel_3 = create_tracker_sub_panel(tracker_panel)
	horiz_sizer_1 = create_tracker_horizontal_sizer()
	horiz_sizer_2 = create_tracker_horizontal_sizer()
	horiz_sizer_3 = create_tracker_horizontal_sizer()
	subpanel_1.SetSizer(horiz_sizer_1)
	subpanel_2.SetSizer(horiz_sizer_2)
	subpanel_3.SetSizer(horiz_sizer_3)
	# creating elements
	tracker_product_name = create_tracker_product_name(subpanel_1, product_name)
	tracker_location = create_tracker_location(subpanel_1, location)
	tracker_max_price = create_tracker_max_price(subpanel_1, max_price)
	tracker_active_time_label = create_tracker_active_time_label(subpanel_2)
	tracker_active_time = create_tracker_active_time(subpanel_2, tracker_dict)
	tracker_scrape_time_label = create_tracker_scrape_time_label(subpanel_2)
	tracker_scrape_time = create_tracker_scrape_time(subpanel_2, tracker_dict)
	remove_tracker_button = create_remove_tracker_button(subpanel_3, tracker_panel, tracker_dict)
	# putting in sizers
	horiz_sizer_1.Add(tracker_product_name, 2, wx.ALL|wx.EXPAND)
	horiz_sizer_1.Add(tracker_location, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_1.Add(tracker_max_price, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_2.Add(tracker_active_time_label, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_2.Add(tracker_active_time, 2, wx.ALL|wx.EXPAND)
	horiz_sizer_2.Add(tracker_scrape_time_label, 1, wx.ALL|wx.EXPAND)
	horiz_sizer_2.Add(tracker_scrape_time, 2, wx.ALL|wx.EXPAND)
	horiz_sizer_3.Add(remove_tracker_button, 0, wx.ALL|wx.EXPAND)
	tracker_panel_sizer.Add(subpanel_1, 0, wx.ALL|wx.EXPAND, 5)
	tracker_panel_sizer.Add(subpanel_2, 0, wx.ALL|wx.EXPAND, 5)
	tracker_panel_sizer.Add(subpanel_3, 0, wx.ALL|wx.EXPAND, 5)
	return tracker_panel

def generate_trackers_view(parent):
	trackers_view_sizer = create_trackers_view_sizer()
	trackers_view_panel = create_trackers_view_panel(parent)
	trackers_view_panel.SetSizer(trackers_view_sizer)
	trackers_panel_sizer = create_trackers_panel_sizer()
	trackers_panel = create_trackers_panel(trackers_view_panel)
	trackers_panel.SetSizer(trackers_panel_sizer)
	trackers_header = create_trackers_header_text(trackers_view_panel)
	trackers_view_sizer.Add(trackers_header, 0, wx.ALL|wx.EXPAND, 5)
	trackers_view_sizer.Add(trackers_panel, 1, wx.ALL|wx.EXPAND, 5)
	for entry in client_state.tracker_entries:
		tracker = generate_tracker(trackers_panel, entry)
		trackers_panel_sizer.Add(tracker, 0, wx.ALL|wx.EXPAND, 5)
	return trackers_view_panel

def destroy_trackers_view():
	client_state.gui_elements['trackers_view_panel'].Destroy()

def show_trackers_view():
	client_state.gui_elements['trackers_view_panel'].Show()

def hide_trackers_view():
	client_state.gui_elements['trackers_view_panel'].Hide()

for i in range(0, 30):
	kwargs = {
		'product_name': str(i),
		'location': 'city-of-toronto',
		'max_price': None,
		'cycle_time': 1800
	}
	add_tracker_entry(kwargs)