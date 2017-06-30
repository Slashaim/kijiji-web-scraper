"""-----------------------------------------------------------------------------

	notifications.py

	Used to control notifications UI and state.

-----------------------------------------------------------------------------"""

import wx
import re
import time
import asyncio
import threading

import helpers
import client_state


"""-----------------------------------------------------------------------------

	Notifications Options creation
	
-----------------------------------------------------------------------------"""

def create_notifications_options_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_notifications_options_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	client_state.gui_elements['notifications_options_panel'] = panel
	return panel

def create_notifications_label(parent):
	label = wx.StaticText(parent, wx.ID_ANY, "Notifications", style = wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_NONE)
	return label

def clear_all_notifications_button_callback(arg):
	client_state.notification_entries = []
	update_notifications_view()

def create_clear_all_notifications_button(parent):
	button = wx.Button(parent, wx.ID_ANY, "Clear All Notifications")
	button.Bind(wx.EVT_BUTTON, clear_all_notifications_button_callback)
	client_state.gui_elements['clear_all_notifications_button'] = button
	return button

def generate_notifications_options(parent):
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
	return notifications_options_panel


"""-----------------------------------------------------------------------------

	Notifications View creation

-----------------------------------------------------------------------------"""

def create_notifications_view_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_notifications_view_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	client_state.gui_elements['notifications_view_panel'] = panel
	return panel

def create_notifications_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	client_state.gui_elements['notifications_panel_sizer'] = sizer
	return sizer

def create_notifications_panel(parent):
	panel = wx.ScrolledCanvas(parent, wx.ID_ANY, style = wx.VSCROLL)
	panel.SetScrollbars(1, 40, 1, 40)
	client_state.gui_elements['notifications_panel'] = panel
	return panel

def create_notifications_header_text(parent):
	num_notifications = len(client_state.notification_entries)
	displayed = str(num_notifications) + ' notifications found.'
	text = wx.TextCtrl(parent, wx.ID_ANY, displayed, style = wx.BORDER_NONE|wx.TE_READONLY)
	client_state.gui_elements['notifications_header_text'] = text
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
		panel.Destroy()
		client_state.notification_entries.remove(entry)
		num_notifications = len(client_state.notification_entries)
		displayed = str(num_notifications) + ' notifications found.'
		client_state.gui_elements['notifications_header_text'].SetValue(displayed)
		client_state.gui_elements['main_frame'].Layout()
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
	ad_price = helpers.convert_price_to_display(notification_dict.get('ad_price'))
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
	else:
		raise ValueError('Invalid notification type: ' + str(notification_type))

def generate_notifications_view(parent):
	notifications_view_sizer = create_notifications_view_sizer()
	notifications_view_panel = create_notifications_view_panel(parent)
	notifications_view_panel.SetSizer(notifications_view_sizer)
	notifications_panel_sizer = create_notifications_panel_sizer()
	notifications_panel = create_notifications_panel(notifications_view_panel)
	notifications_panel.SetSizer(notifications_panel_sizer)
	notifications_header = create_notifications_header_text(notifications_view_panel)
	notifications_view_sizer.Add(notifications_header, 0, wx.ALL|wx.EXPAND, 5)
	notifications_view_sizer.Add(notifications_panel, 1, wx.ALL|wx.EXPAND, 5)
	for entry in client_state.notification_entries:
		notification_panel = generate_notification(notifications_panel, entry)
		notifications_panel_sizer.Prepend(notification_panel, 0, wx.ALL|wx.EXPAND, 5)
	return notifications_view_panel

def destroy_notifications_view():
	client_state.gui_elements['notifications_view_panel'].Destroy()

def update_notifications_view():
	main_frame = client_state.gui_elements['main_frame']
	main_frame_sizer = client_state.gui_elements['main_frame_sizer']
	destroy_notifications_view()
	notifications_view = generate_notifications_view(main_frame)
	main_frame_sizer.Add(notifications_view, 1, wx.ALL|wx.EXPAND)
	num_notifications = len(client_state.notification_entries)
	displayed = str(num_notifications) + ' notifications found.'
	client_state.gui_elements['notifications_header_text'].SetValue(displayed)
	main_frame.Layout()

def show_notifications_view():
	client_state.gui_elements['notifications_view_panel'].Show()

def hide_notifications_view():
	client_state.gui_elements['notifications_view_panel'].Hide()
