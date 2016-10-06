#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from unittest import TestCase

import util

from tests.redirector import Redirector


class DateTests(TestCase):

    def test_get_list_sorting_key_value_no_date(self):
        expected = util.get_date_string(util.SORTING_NO_DATETIME) + '1'
        self.assertEqual(
            expected,
            util.get_list_sorting_key_value({
                'due': None,
                'priority': 1
            })
        )
        self.assertEqual(
            expected,
            util.get_list_sorting_key_value({
                'due': None,
                'priority': 1
            })
        )

    def test_get_date_for_sorting(self):
        expected = datetime(2016, 10, 4, 11, 17, 45)
        expected_string = util.get_date_string(expected) + '4'
        d = {'due': expected, 'priority': 4}
        actual = util.get_list_sorting_key_value(d)
        self.assertEqual(expected_string, actual)

    def test_get_date_or_datetime_string_no_date(self):
        expected = ''
        self.assertEqual(expected, util.get_date_string(None))
        self.assertEqual(expected, util.get_date_string(''))
        self.assertEqual(expected, util.get_datetime_string(None))
        self.assertEqual(expected, util.get_datetime_string(''))

    def test_get_date_string(self):
        self.assertEqual(
            '2016-09-04',
            util.get_date_string(datetime(2016, 9, 4, 11, 17, 45))
        )

    def test_get_datetime_string(self):
        self.assertEqual(
            '2016-09-04 07:08',
            util.get_datetime_string(datetime(2016, 9, 4, 7, 8, 9))
        )
        self.assertEqual(
            '2016-09-04 14:08',
            util.get_datetime_string(datetime(2016, 9, 4, 14, 8, 9))
        )

    def test_get_datetime_no_date(self):
        expected = None
        self.assertEqual(expected, util.get_datetime(None))
        self.assertEqual(expected, util.get_datetime(''))

    def test_get_datetime(self):
        self.assertEqual(
            datetime(2016, 9, 4, 5, 8, 0),
            util.get_datetime('2016-09-04 05:08:00')
        )


class OutputTests(Redirector):

    def test_valid_priority_number(self):
        for priority in util.ALLOWED_PRIORITIES:
            self.assertTrue(util.valid_priority_number(priority))

    def test_valid_priority_number_string(self):
        for priority in util.ALLOWED_PRIORITIES:
            self.assertTrue(util.valid_priority_number(str(priority)))

    def test_invalid_priority_number_alpha(self):
        return_value = util.valid_priority_number('abc')
        self.assertFalse(return_value)
        self.assertEqual(
            util.PRIORITY_NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_invalid_priority_number_string_float(self):
        return_value = util.valid_priority_number('1.7')
        self.assertFalse(return_value)
        self.assertEqual(
            util.PRIORITY_NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_invalid_priority_number_not_allowed(self):
        return_value = util.valid_priority_number('85')
        self.assertFalse(return_value)
        self.assertEqual(
            util.PRIORITY_NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_invalid_priority_number_too_high(self):
        return_val = util.valid_priority_number(util.PRIORITY_HIGH - 1)
        self.assertFalse(return_val)
        self.assertEqual(
            util.PRIORITY_NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_invalid_priority_number_too_low(self):
        return_value = util.valid_priority_number(util.PRIORITY_LOW + 1)
        self.assertFalse(return_value)
        self.assertEqual(
            util.PRIORITY_NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )
