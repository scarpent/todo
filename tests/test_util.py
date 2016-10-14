#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from unittest import TestCase

import util

from tests.helpers import Redirector


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

    def test_valid_history_number(self):
        self.assertTrue(util.valid_history_number(1, 1))
        self.assertTrue(util.valid_history_number(1, 2))
        self.assertTrue(util.valid_history_number('3', 4))

    def test_invalid_history_number(self):
        self.assertFalse(util.valid_history_number('a', 4))
        self.assertEqual(
            util.HISTORY_NUMBER_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_invalid_history_number_choice(self):
        self.assertFalse(util.valid_history_number(5, 4))
        self.assertEqual(
            util.HISTORY_CHOICE_ERROR,
            self.redirect.getvalue().rstrip()
        )
        self.assertFalse(util.valid_history_number(0, 1))
        self.assertFalse(util.valid_history_number('-1', 3))
        self.assertFalse(util.valid_history_number('87', 50))


class DueDateTests(Redirector):

    def test_get_due_date_with_date(self):
        self.assertEqual(
            datetime(1997, 6, 1, 0),
            util.get_due_date('1997-06-01')
        )
        self.assertEqual(
            datetime(1997, 6, 1, 0, 0),
            util.get_due_date('   1997-06-01   ')
        )
        self.assertEqual(
            datetime(1997, 6, 1),
            util.get_due_date('1997-6-1')
        )

    def test_output_bad_due_date_with_date(self):
        self.assertIsNone(util.get_due_date('2016-14-36'))
        self.assertEqual(
            util.DATE_ERROR,
            self.redirect.getvalue().rstrip()
        )

    def test_bad_due_date(self):
        self.assertIsNone(util.get_due_date('5z'))
        self.assertEqual(
            util.DATE_ERROR,
            self.redirect.getvalue().rstrip()
        )
        self.assertIsNone(util.get_due_date('d4'))

    # with hours, time may change between setting due_date and expected
    # date; using this range will be close enough for our purposes
    def fuzzy_date_match(self, expected_delta, due_date):
        expected = datetime.now() + expected_delta
        self.assertGreater(
            due_date,
            expected - relativedelta(minutes=1)
        )
        self.assertLess(
            due_date,
            expected + relativedelta(minutes=1)
        )

    def test_due_date_hour_delta(self):
        self.fuzzy_date_match(
            relativedelta(hours=10),
            util.get_due_date('10hour')
        )
        self.fuzzy_date_match(
            relativedelta(hours=25),
            util.get_due_date('25hours')
        )
        self.fuzzy_date_match(
            relativedelta(hours=25),
            util.get_due_date('25 hours')
        )
        self.fuzzy_date_match(
            relativedelta(hours=36),
            util.get_due_date('36h')
        )
        self.fuzzy_date_match(
            relativedelta(hours=2),
            util.get_due_date('+2hour')
        )
        self.assertEqual(None, util.get_due_date('10houry'))

    @staticmethod
    def get_expected_datetime(rdelta):
        return datetime.combine(
            date.today(),
            datetime.min.time()
        ) + rdelta

    def test_due_date_day_delta(self):
        self.assertEqual(
            self.get_expected_datetime(relativedelta(days=1)),
            util.get_due_date('1d')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(days=8)),
            util.get_due_date('8')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(days=49)),
            util.get_due_date('49days')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(days=7)),
            util.get_due_date('7 days')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(days=1)),
            util.get_due_date('1day')
        )
        self.assertEqual(None, util.get_due_date('2da'))

    def test_due_date_week_delta(self):
        self.assertEqual(
            self.get_expected_datetime(relativedelta(weeks=2)),
            util.get_due_date('2w')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(weeks=1)),
            util.get_due_date('1week')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(weeks=5)),
            util.get_due_date('5weeks')
        )

    def test_due_date_month_delta(self):
        self.assertEqual(
            self.get_expected_datetime(relativedelta(months=1)),
            util.get_due_date('1month')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(months=3)),
            util.get_due_date('3months')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(months=26)),
            util.get_due_date('26m')
        )
        self.assertEqual(None, util.get_due_date('3monkey'))

    def test_due_date_year_delta(self):
        self.assertEqual(
            self.get_expected_datetime(relativedelta(years=1000)),
            util.get_due_date('1000y')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(years=10)),
            util.get_due_date('10year')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(years=2)),
            util.get_due_date('2years')
        )

    def test_zero(self):
        self.fuzzy_date_match(
            relativedelta(hours=0),
            util.get_due_date('0h')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(days=0)),
            util.get_due_date('0d')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(days=0)),
            util.get_due_date('0')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(weeks=0)),
            util.get_due_date('0w')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(minutes=0)),
            util.get_due_date('0m')
        )
        self.assertEqual(
            self.get_expected_datetime(relativedelta(years=0)),
            util.get_due_date('0y')
        )


class MiscTests(TestCase):

    def test_remove_wrapping_quotes(self):
        # quotes must match
        self.assertEqual('bob', util.remove_wrapping_quotes('"bob"'))
        self.assertEqual('bob', util.remove_wrapping_quotes("'bob'"))
        self.assertEqual(
            'good morning',
            util.remove_wrapping_quotes('"good morning"')
        )
        self.assertEqual('bob"', util.remove_wrapping_quotes('bob"'))
        self.assertEqual("'tis", util.remove_wrapping_quotes("'tis"))
        self.assertEqual(
            '\'bob"',
            util.remove_wrapping_quotes('\'bob"')
        )
