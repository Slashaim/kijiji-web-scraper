"""-----------------------------------------------------------------------------

	client_state.py

	Used to hold application state, accessible between modules.

-----------------------------------------------------------------------------"""

active_view = None


gui_elements = {}
valid_locations = [
	'All of Toronto (GTA)',
	'City of Toronto'
]

ui_to_location = {
	'All of Toronto (GTA)': 'all-of-toronto',
	'City of Toronto': 'city-of-toronto'
}
location_to_ui = {
	'all-of-toronto': 'All of Toronto (GTA)',
	'city-of-toronto': 'City of Toronto'
}

ad_entries = []
notification_entries = []
tracker_entries = []