"""-----------------------------------------------------------------------------
	
	main.py

	Dependencies:
	- wx: GUI library
	- aiohttp: Asynchronous http requests
	- lxml: html parsing

-----------------------------------------------------------------------------"""

import lib.gui


def main():
	lib.gui.instantiate()

if __name__ == "__main__":
	main()