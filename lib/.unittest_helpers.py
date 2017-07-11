"""-----------------------------------------------------------------------------

	unittest_helpers.py

	Unit test coverage for the helpers.py module.

-----------------------------------------------------------------------------"""

import unittest

import helpers


class ClampTest(unittest.TestCase):
	def test_non_constrained_positive(self):
		value = helpers.clamp(5)
		self.assertEqual(value, 5)

	def test_non_constrained_zero(self):
		value = helpers.clamp(0)
		self.assertEqual(value, 0)

	def test_non_constrained_negative(self):
		value = helpers.clamp(-7)
		self.assertEqual(value, -7)

	def test_min_constrained_positive(self):
		value = helpers.clamp(5, minimum = 5)
		self.assertEqual(value, 5)
		value = helpers.clamp(5, minimum = 3)
		self.assertEqual(value, 5)
		value = helpers.clamp(1, minimum = 5)
		self.assertEqual(value, 5)

	def test_min_constrained_negative(self):
		value = helpers.clamp(-7, minimum = -10)
		self.assertEqual(value, -7)
		value = helpers.clamp(-5, minimum = -3)
		self.assertEqual(value, -3)

	def test_max_constrained_positive(self):
		value = helpers.clamp(8, maximum = 10)
		self.assertEqual(value, 8)
		value = helpers.clamp(9, maximum = 7)
		self.assertEqual(value, 7)

	def test_max_constrained_negative(self):
		value = helpers.clamp(-7, maximum = -5)
		self.assertEqual(value, -7)
		value = helpers.clamp(-10, maximum = -15)
		self.assertEqual(value, -15)

	def test_minmax_constrained(self):
		value = helpers.clamp(5, minimum = 3, maximum = 7)
		self.assertEqual(value, 5)
		value = helpers.clamp(7, minimum = 8, maximum = 10)
		self.assertEqual(value, 8)
		value = helpers.clamp(11, minimum = 5, maximum = 9)
		self.assertEqual(value, 9)

	def test_error_raised(self):
		with self.assertRaises(ValueError):
			value = helpers.clamp(6, minimum = 5, maximum = 3)


class ValidProductNameTest(unittest.TestCase):
	def test_valid_matches(self):
		is_valid = helpers.valid_product_name('dfagadg')
		self.assertIs(is_valid, True)
		is_valid = helpers.valid_product_name('hello world')
		self.assertIs(is_valid, True)
		is_valid = helpers.valid_product_name('4gf 09ur fa09')
		self.assertIs(is_valid, True)
		is_valid = helpers.valid_product_name('HOog OIg')
		self.assertIs(is_valid, True)
		is_valid = helpers.valid_product_name('    dgo gkj  ')

	def test_invalid_matches(self):
		is_valid = helpers.valid_product_name('')
		self.assertIs(is_valid, False)
		is_valid = helpers.valid_product_name('   ')
		self.assertIs(is_valid, False)
		is_valid = helpers.valid_product_name('&faoj')
		self.assertIs(is_valid, False)

	def test_invalid_types(self):
		is_valid = helpers.valid_product_name(None)
		self.assertIs(is_valid, False)
		is_valid = helpers.valid_product_name(True)
		self.assertIs(is_valid, False)
		is_valid = helpers.valid_product_name(369)
		self.assertIs(is_valid, False)


class GetMaxAdsTest(unittest.TestCase):
	def test_valid_numbers(self):
		max_ads = helpers.get_max_ads('30')
		self.assertEqual(max_ads, 30)
		max_ads = helpers.get_max_ads('5')
		self.assertEqual(max_ads, 5)

	def test_invalid_numbers(self):
		max_ads = helpers.get_max_ads('-325')
		self.assertIs(max_ads, None)

	def test_invalid_types(self):
		with self.assertRaises(TypeError):
			helpers.get_max_ads(None)


class GetMaxPriceTest(unittest.TestCase):
	def test_valid_prices(self):
		price = helpers.get_max_price('')
		self.assertIs(price, None)
		price = helpers.get_max_price('0')
		self.assertIs(price, None)
		price = helpers.get_max_price('235')
		self.assertEqual(price, 235.00)
		price = helpers.get_max_price('2344.75')
		self.assertEqual(price, 2344.75)

	def test_invalid_prices(self):
		price = helpers.get_max_price('-325')
		self.assertIs(price, False)


class ConvertPriceToDisplayTest(unittest.TestCase):
	def test_valid_prices(self):
		display = helpers.convert_price_to_display(35)
		self.assertEqual(display, '$35.00')
		display = helpers.convert_price_to_display(234.6)
		self.assertEqual(display, '$234.60')
		display = helpers.convert_price_to_display(2.57)
		self.assertEqual(display, '$2.57')
		display = helpers.convert_price_to_display(4325646.43)
		self.assertEqual(display, '$4,325,646.43')
		display = helpers.convert_price_to_display('no price given')
		self.assertEqual(display, 'no price given')

	def test_invalid_prices(self):
		display = helpers.convert_price_to_display(None)
		self.assertEqual(display, '')


if __name__ == '__main__':
	unittest.main(verbosity = 2)