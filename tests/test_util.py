#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from unittest import TestCase

import util


class UtilTests(TestCase):

    def test_get_date_for_sorting_no_date(self):
        expected = util.SORTING_NO_DATETIME
        self.assertEqual(
            expected,
            util.get_due_date_for_sorting({'due': None})
        )
        self.assertEqual(
            expected,
            util.get_due_date_for_sorting({'due': ''})
        )

    def test_get_date_for_sorting(self):
        expected = datetime(2016, 10, 4, 11, 17, 45)
        d = {'due': expected}
        actual = util.get_due_date_for_sorting(d)
        self.assertEqual(expected, actual)

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
