"""-----------------------------------------------------------------------------

	trackers.py

	Used to control trackers UI and state.

-----------------------------------------------------------------------------"""

import wx
import time
import datetime
import asyncio
import threading

import lib.kijiji_scraper
import lib.helpers
import lib.client_state
import lib.notifications


"""-----------------------------------------------------------------------------

	Helpers

-----------------------------------------------------------------------------"""

def get_notification_title_from_tracker(entry):
	product_name = entry['product_name']
	given_location = entry.get('location')
	location = lib.client_state.location_to_ui.get(given_location)
	given_max_price = entry.get('max_price')
	max_price = lib.helpers.convert_price_to_display(given_max_price)
	if given_max_price and location:
		return product_name + ' in ' + location + ' under ' + max_price
	elif location:
		return product_name + ' in ' + location
	elif max_price:
		return product_name + ' under ' + max_price
	else:
		return product_name

def update_header_text():
	num_trackers = len(lib.client_state.tracker_entries)
	displayed = 'No trackers found.'
	if num_trackers == 1:
		displayed = str(num_trackers) + ' tracker found.'
	elif num_trackers > 1:
		displayed = str(num_trackers) + ' trackers found.'
	lib.client_state.gui_elements['trackers_header_text'].SetValue(displayed)


"""-----------------------------------------------------------------------------

	Trackers Options creation
	
-----------------------------------------------------------------------------"""

def create_trackers_options_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_trackers_options_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	lib.client_state.gui_elements['trackers_options_panel'] = panel
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
	lib.client_state.gui_elements['tracker_product_name_text_box'] = text_box
	return text_box

def create_tracker_max_price_text_box_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Max Price:", style = wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_NONE)
	return label

def create_tracker_max_price_text_box(parent):
	text_box = wx.TextCtrl(parent, wx.ID_ANY)
	lib.client_state.gui_elements['tracker_max_price_text_box'] = text_box
	return text_box

def create_tracker_location_choice(parent):
	choice = wx.Choice(parent, wx.ID_ANY, choices = lib.client_state.valid_locations)
	choice.SetSelection(0)
	lib.client_state.gui_elements['tracker_location_choice'] = choice
	return choice

def tracker_button_callback(arg):
	tracker_product_name_text_box = lib.client_state.gui_elements['tracker_product_name_text_box']
	tracker_max_price_text_box = lib.client_state.gui_elements['tracker_max_price_text_box']
	tracker_location_choice = lib.client_state.gui_elements['tracker_location_choice']
	tracker_message = lib.client_state.gui_elements['tracker_message']
	# setting initial gui state
	tracker_product_name_text_box.SetBackgroundColour(wx.Colour(255, 255, 255))
	tracker_product_name_text_box.Refresh()
	tracker_message.SetValue('')
	# getting initial gui state and checking for valid inputs
	given_product_name = tracker_product_name_text_box.GetLineText(lineNo = 0)
	given_max_price = lib.helpers.get_max_price(tracker_max_price_text_box.GetLineText(lineNo = 0))
	given_location = tracker_location_choice.GetSelection()
	location = lib.client_state.ui_to_location.get(tracker_location_choice.GetString(given_location))
	if len(lib.client_state.tracker_entries) >= lib.client_state.max_trackers:
		tracker_message.SetValue('Max trackers (' + str(lib.client_state.max_trackers) + ') reached.' )
		return
	if not lib.helpers.valid_product_name(given_product_name):
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
	entry = add_tracker_entry({
		'product_name': given_product_name,
		'location': location,
		'cycle_time': 900,
		'max_price': given_max_price
	})
	trackers_panel = lib.client_state.gui_elements['trackers_panel']
	tracker_panel = generate_tracker(trackers_panel, entry)
	trackers_panel_sizer = lib.client_state.gui_elements['trackers_panel_sizer']
	trackers_panel_sizer.Add(tracker_panel, 0, wx.ALL|wx.EXPAND, 5)
	update_header_text()
	main_frame = lib.client_state.gui_elements['main_frame']
	main_frame.Layout()

def create_tracker_button(parent):
	button = wx.Button(parent, wx.ID_ANY, "Create New Tracker")
	button.Bind(wx.EVT_BUTTON, tracker_button_callback)
	lib.client_state.gui_elements['tracker_button'] = button
	return button

def create_tracker_message(parent):
	label = wx.TextCtrl(parent, wx.ID_ANY, "", style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
	label.SetBackgroundColour(wx.Colour(240,240,240))
	lib.client_state.gui_elements['tracker_message'] = label
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
	trackers_options_sizer.Add(tracker_message, 0, wx.ALL|wx.EXPAND, 5)
	lib.client_state.gui_elements['trackers_options_panel'] = trackers_options_panel
	return trackers_options_panel

def show_trackers_options():
	lib.client_state.gui_elements['trackers_options_panel'].Show()

def hide_trackers_options():
	lib.client_state.gui_elements['trackers_options_panel'].Hide()


"""-----------------------------------------------------------------------------

	Trackers actions
	
-----------------------------------------------------------------------------"""

def get_new_ads_for_tracker(entry):
	product_name = entry.get('product_name')
	location = entry.get('location')
	max_price = entry.get('max_price')
	viewed_ad_ids = entry.get('viewed_ad_ids')
	def list_check(li):
		return len(li) >= 10

	def post_proc(li):
		return [x for x in li if x['ad_id'] not in viewed_ad_ids][:10]

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

	def entry_break(ad):
		return ad['ad_id'] in viewed_ad_ids

	try:
		ads = lib.kijiji_scraper.get_ad_entries_from_constraints(
			parameters = {
				'product_name': product_name,
				'location': location,
				'show_top_ads': False,
				'show_third_party_ads': False,
				'only_new_ads': True,
				'entry_incl': entry_incl,
				'entry_break': entry_break,
				'post_proc': post_proc,
				'num_pages_per_cycle': 1
			},
			list_check = list_check
		)
		for ad in ads:
			viewed_ad_ids.add(ad['ad_id'])
		return ads
	except asyncio.TimeoutError:
		return []

def init_tracker_viewed_ads(entry):
	product_name = entry.get('product_name')
	location = entry.get('location')
	max_price = entry.get('max_price')
	viewed_ad_ids = entry.get('viewed_ad_ids')
	def list_check(li):
		return len(li) >= 1

	def entry_incl(ad):
		# determining if class allowed
		html_class = ad.get('html_class')
		class_allowed = html_class == 'normal'
		return class_allowed

	try:
		ads = lib.kijiji_scraper.get_ad_entries_from_constraints(
			parameters = {
				'product_name': product_name,
				'location': location,
				'show_top_ads': False,
				'show_third_party_ads': False,
				'only_new_ads': True,
				'entry_incl': entry_incl,
				'num_pages_per_cycle': 1
			},
			list_check = list_check
		)
		for ad in ads:
			viewed_ad_ids.add(ad['ad_id'])
		return ads
	except asyncio.TimeoutError:
		return []

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
	try:
		clamped_active_time = lib.helpers.clamp(entry['active_time'], minimum = 0)
		formatted_active_time = str(datetime.timedelta(seconds = round(clamped_active_time)))
		entry['gui_active_time'].SetValue(formatted_active_time)
		clamped_time_to_next_scrape = lib.helpers.clamp(entry['time_to_next_scrape'], minimum = 0)
		formatted_time_to_next_scrape = str(datetime.timedelta(seconds = round(clamped_time_to_next_scrape)))
		entry['gui_scrape_time'].SetValue(formatted_time_to_next_scrape)
	except KeyError:
		pass

def ad_update_tracker_entry(entry):
	scrape_on_next = entry['scrape_on_next']
	if scrape_on_next:
		entry['scrape_on_next'] = False
		entry['last_scrape_time'] = time.perf_counter()
		# updating the notifications gui in a separate thread prevents it from hanging
		def gui_update_func():
			ads = get_new_ads_for_tracker(entry)
			for ad in ads:
				notification_title = get_notification_title_from_tracker(entry)
				price = lib.helpers.convert_price_to_display(ad.get('price'))
				new_notification = {
					'notification_type': 'newad',
					'front_text': 'New Ad',
					'notification_title': notification_title,
					'ad_price': price,
					'ad_title': ad.get('title'),
					'ad_url': ad.get('url'),
					'start_time': time.perf_counter()
				}
				lib.client_state.notification_entries.appendleft(new_notification)
			if len(ads) > 0:
				lib.notifications.update_notifications_view()
				main_frame = lib.client_state.gui_elements['main_frame']
				if main_frame.IsIconized():
					main_frame.RequestUserAttention(flags = wx.USER_ATTENTION_INFO)
		thread = threading.Thread(None, target = gui_update_func)
		thread.start()


"""-----------------------------------------------------------------------------

	Trackers View creation

-----------------------------------------------------------------------------"""

def create_trackers_view_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_trackers_view_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	lib.client_state.gui_elements['trackers_view_panel'] = panel
	return panel

def create_trackers_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	lib.client_state.gui_elements['trackers_panel_sizer'] = sizer
	return sizer

def create_trackers_panel(parent):
	panel = wx.ScrolledCanvas(parent, wx.ID_ANY, style = wx.VSCROLL)
	panel.SetScrollbars(1, 40, 1, 40)
	lib.client_state.gui_elements['trackers_panel'] = panel
	return panel

def create_trackers_header_text(parent):
	text = wx.TextCtrl(parent, wx.ID_ANY, '', style = wx.BORDER_NONE|wx.TE_READONLY)
	lib.client_state.gui_elements['trackers_header_text'] = text
	update_header_text()
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
	displayed = max_price + ' max'
	text = wx.TextCtrl(parent, wx.ID_ANY, displayed, style = wx.TE_READONLY|wx.BORDER_NONE|wx.TE_NO_VSCROLL|wx.TE_RICH)
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
		lib.client_state.tracker_entries.remove(entry)
		update_header_text()
		lib.client_state.gui_elements['main_frame'].Layout()
	return callback

def create_remove_tracker_button(parent, panel, entry):
	button = wx.Button(parent, wx.ID_ANY, "Remove Tracker")
	callback = tracker_remove_tracker_button_callback_generator(panel, entry)
	button.Bind(wx.EVT_BUTTON, callback)
	return button

def generate_tracker(parent, tracker_dict):
	product_name = tracker_dict.get('product_name')
	location = lib.client_state.location_to_ui[tracker_dict['location']]
	max_price = lib.helpers.convert_price_to_display(tracker_dict.get('max_price'))
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


"""-----------------------------------------------------------------------------

	Public tracker actions

-----------------------------------------------------------------------------"""

def add_tracker_entry(tracker_dict):
	entry = {
		'product_name': tracker_dict.get('product_name'),
		'location': tracker_dict.get('location'),
		'max_price': tracker_dict.get('max_price'),
		'start_time': 0,
		'last_scrape_time': 0,
		'active_time': 0,
		'time_to_next_scrape': 0,
		'cycle_time': tracker_dict.get('cycle_time'),
		'scrape_on_next': False,
		'viewed_ad_ids': set()
	}
	# initialising new tracker with set of ads
	init_tracker_viewed_ads(entry)
	entry['start_time'] = time.perf_counter()
	lib.client_state.tracker_entries.append(entry)
	return entry

def create_tracker_time_update_thread():
	def time_update_loop():
		while lib.client_state.app_open:
			try:
				for entry in lib.client_state.tracker_entries:
					time_update_tracker_entry(entry)
					gui_update_tracker_entry(entry)
			# tracker_entries mutated during iteration
			except RuntimeError:
				pass
			time.sleep(0.8)
	thread = threading.Thread(None, target = time_update_loop)
	return thread

def create_tracker_ad_update_thread():
	def ad_update_loop():
		while lib.client_state.app_open:
			try:
				for entry in lib.client_state.tracker_entries:
					ad_update_tracker_entry(entry)
			# tracker_entries mutated during iteration
			except RuntimeError:
				pass
			time.sleep(1)
	thread = threading.Thread(None, target = ad_update_loop)
	return thread


"""-----------------------------------------------------------------------------

	Public Functions

-----------------------------------------------------------------------------"""

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
	for entry in lib.client_state.tracker_entries:
		tracker = generate_tracker(trackers_panel, entry)
		trackers_panel_sizer.Add(tracker, 0, wx.ALL|wx.EXPAND, 5)
	return trackers_view_panel

def show_trackers_view():
	lib.client_state.gui_elements['trackers_view_panel'].Show()

def hide_trackers_view():
	lib.client_state.gui_elements['trackers_view_panel'].Hide()