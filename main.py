"""-----------------------------------------------------------------------------
	
	main.py

	Started on June 18 2017.

-----------------------------------------------------------------------------"""

import os
import mod


dir_name = os.path.dirname(os.path.abspath(__file__))
test_file = dir_name + "/" + "test.txt"

def main():
	print("Hello world!")
	# gui i/o + options
	# web scraping tools
	# search
	with open(test_file) as f:
		for line in f:
			print(line)



if __name__ == "__main__":
	main()