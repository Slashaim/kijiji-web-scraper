"""-----------------------------------------------------------------------------

	gui.py

	Controls the creation of the GUI.
	
-----------------------------------------------------------------------------"""

import wx

import lib.scraping
import lib.notifications
import lib.trackers
import lib.client_state


"""-----------------------------------------------------------------------------

	App creation
	
-----------------------------------------------------------------------------"""

def create_app():
	app = wx.App(False)
	def app_on_exit():
		lib.client_state.app_open = False
	lib.client_state.gui_elements['app'] = app
	app.OnExit = app_on_exit
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

def scrape_view_button_callback(arg):
	change_view('scraping')

def create_scrape_view_button(parent):
	button = wx.Button(parent, wx.ID_ANY, "Scraping View")
	button.Bind(wx.EVT_BUTTON, scrape_view_button_callback)
	lib.client_state.gui_elements['scrape_view_button'] = button
	return button

def notifications_view_button_callback(arg):
	change_view('notifications')

def create_notifications_view_button(parent):
	button = wx.Button(parent, wx.ID_ANY, "Notifications View")
	button.Bind(wx.EVT_BUTTON, notifications_view_button_callback)
	lib.client_state.gui_elements['notifications_view_button'] = button
	return button

def trackers_view_button_callback(arg):
	change_view('trackers')

def create_trackers_view_button(parent):
	button = wx.Button(parent, wx.ID_ANY, "Trackers View")
	button.Bind(wx.EVT_BUTTON, trackers_view_button_callback)
	lib.client_state.gui_elements['trackers_view_button'] = button
	return button

def generate_views_options(parent):
	# creating panel and setting sizer
	views_panel = create_views_panel(parent)
	views_sizer = create_views_sizer()
	views_panel.SetSizer(views_sizer)
	# creating elements
	views_label = create_views_label(views_panel)
	scrape_view_button = create_scrape_view_button(views_panel)
	notifications_view_button = create_notifications_view_button(views_panel)
	trackers_view_button = create_trackers_view_button(views_panel)
	# adding to sizer
	views_sizer.Add(views_label, 0, wx.ALL|wx.EXPAND)
	views_sizer.Add(scrape_view_button, 0, wx.ALL|wx.EXPAND, 5)
	views_sizer.Add(notifications_view_button, 0, wx.ALL|wx.EXPAND, 5)
	views_sizer.Add(trackers_view_button, 0, wx.ALL|wx.EXPAND, 5)
	lib.client_state.gui_elements['views_options_panel'] = views_panel
	return views_panel


"""-----------------------------------------------------------------------------

	Options Panel creation
	
-----------------------------------------------------------------------------"""

def create_options_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_options_panel(parent):
	panel = wx.ScrolledCanvas(parent, wx.ID_ANY, size = (300, 10000))
	panel.SetScrollbars(1, 10, 1, 10)
	return panel

def generate_options_panel(parent):
	# setting up panel and sizer
	options_panel = create_options_panel(parent)
	options_sizer = create_options_panel_sizer()
	options_panel.SetSizer(options_sizer)
	lib.client_state.gui_elements['options_panel'] = options_panel
	lib.client_state.gui_elements['options_panel_sizer'] = options_sizer
	views_options = generate_views_options(options_panel)
	scraping_options = lib.scraping.generate_scrape_options(options_panel)
	notifications_options = lib.notifications.generate_notifications_options(options_panel)
	trackers_options = lib.trackers.generate_trackers_options(options_panel)
	options_sizer.Add(views_options, 0, wx.ALL|wx.EXPAND)
	options_sizer.Add(scraping_options, 0, wx.ALL|wx.EXPAND)
	options_sizer.Add(notifications_options, 0, wx.ALL|wx.EXPAND)
	options_sizer.Add(trackers_options, 0, wx.ALL|wx.EXPAND)
	scraping_options.Hide()
	notifications_options.Hide()
	trackers_options.Hide()
	return options_panel


"""-----------------------------------------------------------------------------

	Options Panel actions
	
-----------------------------------------------------------------------------"""

def change_options_panel_state(new_view):
	lib.scraping.hide_scrape_options()
	lib.notifications.hide_notifications_options()
	lib.trackers.hide_trackers_options()
	if new_view == 'scraping':
		lib.scraping.show_scrape_options()
	elif new_view == 'notifications':
		lib.notifications.show_notifications_options()
	elif new_view == 'trackers':
		lib.trackers.show_trackers_options()


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
	main_frame = create_main_frame()
	options_panel = generate_options_panel(main_frame)
	sizer = create_main_frame_sizer()
	sizer.Add(options_panel, 0, wx.ALL|wx.EXPAND)
	main_frame.SetSizer(sizer)
	lib.client_state.gui_elements['main_frame'] = main_frame
	lib.client_state.gui_elements['main_frame_sizer'] = sizer
	return main_frame


"""-----------------------------------------------------------------------------

	State changes
	
-----------------------------------------------------------------------------"""

def instantiate_all_views():
	main_frame = lib.client_state.gui_elements['main_frame']
	main_frame_sizer = lib.client_state.gui_elements['main_frame_sizer']
	scrape_view = lib.scraping.generate_scrape_view(main_frame)
	notifications_view = lib.notifications.generate_notifications_view(main_frame)
	trackers_view = lib.trackers.generate_trackers_view(main_frame)
	main_frame_sizer.Add(scrape_view, 1, wx.ALL|wx.EXPAND)
	main_frame_sizer.Add(notifications_view, 1, wx.ALL|wx.EXPAND)
	main_frame_sizer.Add(trackers_view, 1, wx.ALL|wx.EXPAND)
	lib.scraping.hide_scrape_view()
	lib.notifications.hide_notifications_view()
	lib.trackers.hide_trackers_view()

def change_view(new_view):
	active_view = lib.client_state.active_view
	if new_view != active_view:
		lib.scraping.hide_scrape_view()
		lib.notifications.hide_notifications_view()
		lib.trackers.hide_trackers_view()
		# create new view and display relevant options
		main_frame = lib.client_state.gui_elements['main_frame']
		main_frame_sizer = lib.client_state.gui_elements['main_frame_sizer']
		change_options_panel_state(new_view)
		if new_view == 'scraping':
			lib.scraping.show_scrape_view()
			lib.client_state.active_view = 'scraping'
		elif new_view == 'notifications':
			lib.notifications.show_notifications_view()
			lib.client_state.active_view = 'notifications'
		elif new_view == 'trackers':
			lib.trackers.show_trackers_view()
			lib.client_state.active_view = 'trackers'
		main_frame.Layout()

def instantiate():
	app = create_app()
	main_frame = generate_main_frame()
	instantiate_all_views()
	change_view('scraping')
	lib.notifications.create_instantiate_panels_thread() # costly, new thread so that app open does not stall
	lib.notifications.create_notification_gui_update_thread()
	lib.trackers.create_tracker_time_update_thread()
	lib.trackers.create_tracker_ad_update_thread()
	app.MainLoop()
	