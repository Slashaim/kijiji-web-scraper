"""-----------------------------------------------------------------------------

	client_state.py

	Used to hold application state, accessible between modules.

-----------------------------------------------------------------------------"""

import collections

# app state
active_view = None
gui_elements = {}
app_open = True
viewed_ad_ids = set()

# view-specific state
max_ads = 50
ad_gui_panels = []
ad_entries = []
max_notifications = 100
notification_gui_panels = []
notification_entries = collections.deque(maxlen = max_notifications)
max_trackers = 10
tracker_entries = []

# for location list boxes
valid_locations = [
	'All of Toronto (GTA)',
	'City of Toronto',
	'Markham / York Region',
	'Mississauga / Peel Region',
	'Oakville / Halton Region',
	'Oshawa / Durham Region'
]

ui_to_location = {
	'All of Toronto (GTA)': 'all-of-toronto',
	'Toronto (GTA)': 'all-of-toronto',
	'Canada': 'canada',
	'City of Toronto': 'city-of-toronto',
	'Markham / York Region': 'markham-york-region',
	'Mississauga / Peel Region': 'mississauga-peel-region',
	'Oakville / Halton Region': 'oakville-halton-region',
	'Oshawa / Durham Region': 'oshawa-durham-region'
}
location_to_ui = {
	'canada': 'Canada',
	'all-of-toronto': 'All of Toronto (GTA)',
	'city-of-toronto': 'City of Toronto',
	'markham-york-region': 'Markham / York Region',
	'mississauga-peel-region': 'Mississauga / Peel Region',
	'oakville-halton-region': 'Oakville / Halton Region',
	'oshawa-durham-region': 'Oshawa / Durham Region'
}