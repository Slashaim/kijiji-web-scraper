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

# ADDTO: any new locations and their conversions
# for location list boxes
valid_locations = [
	'All of Toronto (GTA)',
	'City of Toronto',
	'Markham / York Region',
	'Mississauga / Peel Region',
	'Oakville / Halton Region',
	'Oshawa / Durham Region'
]