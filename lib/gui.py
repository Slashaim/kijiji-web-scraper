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
	# overriding the OnExit method appears to cause a TypeError: invalid argument
	# to sipBadCatcherResult() exception.
	app.OnExit = app_on_exit
	return app


"""-----------------------------------------------------------------------------

	Views Options creation

	Creates the part of the UI responsible for switching between 'views' or
	modes.
	
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

# ADDTO: Any new views need to have their buttons generated and placed here.
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

	Creates the options panel, ie. everything on the left side of the UI.
	
-----------------------------------------------------------------------------"""

def create_options_panel_sizer():
	sizer = wx.BoxSizer(wx.VERTICAL)
	return sizer

def create_options_panel(parent):
	panel = wx.ScrolledCanvas(parent, wx.ID_ANY, size = (300, 10000))
	panel.SetScrollbars(1, 10, 1, 10)
	return panel

# ADDTO: Any view-specific options need to be generated and placed here.
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
	hide_all_options()
	return options_panel


"""-----------------------------------------------------------------------------

	Options Panel actions
	
-----------------------------------------------------------------------------"""

# ADDTO: All view-specific options need to be hidden here.
def hide_all_options():
	lib.scraping.hide_scrape_options()
	lib.notifications.hide_notifications_options()
	lib.trackers.hide_trackers_options()

# ADDTO: All view-specific options need a case where they are shown.
def change_options_panel_state(new_view):
	hide_all_options()
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
	lib.client_state.gui_elements['main_frame'] = frame
	return frame

def create_main_frame_sizer():
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	lib.client_state.gui_elements['main_frame_sizer'] = sizer
	return sizer

def create_main_view_panel(parent):
	panel = wx.Panel(parent, wx.ID_ANY)
	lib.client_state.gui_elements['main_view_panel'] = panel
	return panel

def create_main_view_sizer():
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	lib.client_state.gui_elements['main_view_sizer'] = sizer
	return sizer

def generate_main_frame():
	main_frame = create_main_frame()
	options_panel = generate_options_panel(main_frame)
	main_view_panel = create_main_view_panel(main_frame)
	main_view_sizer = create_main_view_sizer()
	main_view_panel.SetSizer(main_view_sizer)
	sizer = create_main_frame_sizer()
	sizer.Add(options_panel, 0, wx.ALL|wx.EXPAND)
	sizer.Add(main_view_panel, 1, wx.ALL|wx.EXPAND)
	main_frame.SetSizer(sizer)
	return main_frame


"""-----------------------------------------------------------------------------

	State changes
	
-----------------------------------------------------------------------------"""

# ADDTO: All views need to be hidden here.
def hide_all_views():
	lib.scraping.hide_scrape_view()
	lib.notifications.hide_notifications_view()
	lib.trackers.hide_trackers_view()

# ADDTO: All views need to be created and placed here.
def instantiate_all_views():
	main_frame = lib.client_state.gui_elements['main_frame']
	main_frame_sizer = lib.client_state.gui_elements['main_frame_sizer']
	main_view_panel = lib.client_state.gui_elements['main_view_panel']
	main_view_sizer = lib.client_state.gui_elements['main_view_sizer']
	scrape_view = lib.scraping.generate_scrape_view(main_view_panel)
	notifications_view = lib.notifications.generate_notifications_view(main_view_panel)
	trackers_view = lib.trackers.generate_trackers_view(main_view_panel)
	main_view_sizer.Add(scrape_view, 1, wx.ALL|wx.EXPAND)
	main_view_sizer.Add(notifications_view, 1, wx.ALL|wx.EXPAND)
	main_view_sizer.Add(trackers_view, 1, wx.ALL|wx.EXPAND)
	hide_all_views()

# ADDTO: All views need a case in which they are shown.
def change_view(new_view):
	active_view = lib.client_state.active_view
	if new_view != active_view:
		hide_all_views()
		# create new view and display relevant options
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
		lib.client_state.gui_elements['main_frame'].Layout()


"""-----------------------------------------------------------------------------

	GUI creation
	
-----------------------------------------------------------------------------"""

def instantiate():
	app = create_app()
	main_frame = generate_main_frame()
	instantiate_all_views()
	# instantiating many new panels is costly, so they are run here so that
	# app startup does not hang
	def instantiate_panels():
		lib.scraping.instantiate_panels()
		lib.notifications.instantiate_panels()
	wx.CallLater(0, instantiate_panels)
	# running threads to update gui and automatic scraping
	lib.notifications.create_notification_gui_update_thread().start()
	lib.trackers.create_tracker_time_update_thread().start()
	lib.trackers.create_tracker_ad_update_thread().start()
	app.MainLoop()
	