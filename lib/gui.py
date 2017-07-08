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
	lib.client_state.gui_elements['views_options_panel'] = views_panel
	return views_panel


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
	# setting up panel and sizer
	options_panel = create_options_panel(parent)
	options_sizer = create_options_panel_sizer()
	options_panel.SetSizer(options_sizer)
	lib.client_state.gui_elements['options_panel'] = options_panel
	lib.client_state.gui_elements['options_panel_sizer'] = options_sizer
	return options_panel


"""-----------------------------------------------------------------------------

	Options Panel actions
	
-----------------------------------------------------------------------------"""

def change_options_panel_state(new_view):
	options_panel = lib.client_state.gui_elements['options_panel']
	options_sizer = lib.client_state.gui_elements['options_panel_sizer']
	options_sizer.Clear(delete_windows = True)
	views_options = generate_views_options(options_panel)
	options_sizer.Add(views_options, 0, wx.ALL|wx.EXPAND)
	options_sizer.AddSpacer(20)
	if new_view == 'scraping':
		scraping_options = lib.scraping.generate_scrape_options(options_panel)
		options_sizer.Add(scraping_options, 0, wx.ALL|wx.EXPAND)
	elif new_view == 'notifications':
		notifications_options = lib.notifications.generate_notifications_options(options_panel)
		options_sizer.Add(notifications_options, 0, wx.ALL|wx.EXPAND)
	elif new_view == 'trackers':
		trackers_options = lib.trackers.generate_trackers_options(options_panel)
		options_sizer.Add(trackers_options, 0, wx.ALL|wx.EXPAND)


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

def hide_all_views():
	lib.scraping.hide_scrape_view()
	lib.notifications.hide_notifications_view()
	lib.trackers.hide_trackers_view()

def change_view(new_view):
	active_view = lib.client_state.active_view
	if new_view != active_view:
		if active_view == 'scraping':
			lib.scraping.hide_scrape_view()
		elif active_view == 'notifications':
			lib.notifications.hide_notifications_view()
		elif active_view == 'trackers':
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
	hide_all_views()
	change_view('scraping')
	lib.notifications.create_notification_gui_update_thread()
	lib.trackers.create_tracker_time_update_thread()
	lib.trackers.create_tracker_ad_update_thread()
	app.MainLoop()

def main():
	instantiate()

if __name__ == "__main__":
	main()
	