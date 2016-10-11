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
            '2016-09-04 07:08:09',
            util.get_datetime_string(datetime(2016, 9, 4, 7, 8, 9))
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
        self.assertEqual(
            datetime(2016, 9, 4, 5, 8, 0),
            util.get_datetime('2016-9-4 05:08:00')
        )
        with self.assertRaises(ValueError):
            util.get_datetime('2016-13-04 05:08:00')

    def test_get_datetime_from_date_only(self):
        self.assertEqual(
            datetime(2016, 9, 4),
            util.get_datetime_from_date_only_string('2016-09-04')
        )
        self.assertEqual(
            datetime(2016, 9, 4),
            util.get_datetime_from_date_only_string('2016-9-4')
        )
        with self.assertRaises(ValueError):
            util.get_datetime('2016-14-36')


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


class DueDateTests(Redirector):

    def test_get_due_date_with_date(self):
        self.assertEqual(
            datetime(1997, 6, 1, 0),
            util.get_due_date('1997-06-01', datetime.today())
        )
        self.assertEqual(
            datetime(1997, 6, 1, 0, 0),
            util.get_due_date('   1997-06-01   ', datetime.today())
        )
        self.assertEqual(
            datetime(1997, 6, 1),
            util.get_due_date('1997-6-1', datetime.today())
        )

    def test_output_bad_due_date_with_date(self):
        self.assertIsNone(
            util.get_due_date('2016-14-36', datetime.today())
        )
        self.assertEqual(
            util.DUE_DATE_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_bad_due_date(self):
        # later we may want to handle 0 without a letter, but for now:
        self.assertIsNone(util.get_due_date('0', datetime.today()))
        self.assertEqual(
            util.DUE_DATE_ERROR,
            self.redirect.getvalue().rstrip()
        )
        self.assertIsNone(util.get_due_date('5z', datetime.today()))
        self.assertIsNone(util.get_due_date('d4', datetime.today()))

    def test_due_date_hour_delta(self):
        self.assertEqual(
            datetime(2015, 4, 7, 16, 5, 22),
            util.get_due_date('10happy', datetime(2015, 4, 7, 6, 5, 22))
        )
        self.assertEqual(
            datetime(2015, 4, 8, 7, 5, 22),
            util.get_due_date('25h', datetime(2015, 4, 7, 6, 5, 22))
        )

    def test_due_date_day_delta(self):
        self.assertEqual(
            datetime(2015, 4, 7),
            util.get_due_date('1d', datetime(2015, 4, 6))
        )
        self.assertEqual(
            datetime(2015, 4, 7),
            util.get_due_date('1day', datetime(2015, 4, 6, 5, 4, 3))
        )
        self.assertEqual(
            datetime(2006, 1, 30),
            util.get_due_date(
                '5 days',
                datetime(2006, 1, 25, 21, 30, 59, 445566)
            )
        )

    def test_due_date_week_delta(self):
        self.assertEqual(
            datetime(2014, 1, 10),
            util.get_due_date('2w', datetime(2013, 12, 27, 5))
        )

    def test_due_date_month_delta(self):
        self.assertEqual(
            datetime(2016, 2, 29),
            util.get_due_date('1month', datetime(2016, 1, 30))
        )
        self.assertEqual(
            datetime(2018, 3, 15),
            util.get_due_date('26m', datetime(2016, 1, 15))
        )

    def test_due_date_year_delta(self):
        self.assertEqual(
            datetime(2999, 12, 31),
            util.get_due_date('1000y', datetime(1999, 12, 31, 1, 1, 1))
        )

    def test_due_date_plus_minus_delta(self):
        self.assertEqual(
            datetime(2015, 4, 11),
            util.get_due_date('+5d', datetime(2015, 4, 6))
        )
        self.assertEqual(
            datetime(2015, 4, 1),
            util.get_due_date('-5d', datetime(2015, 4, 6, 5, 4, 3))
        )
        self.assertEqual(
            datetime(2015, 4, 7, 1, 5),
            util.get_due_date('-5hour', datetime(2015, 4, 7, 6, 5))
        )
