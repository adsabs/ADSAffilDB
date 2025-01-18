import unittest

import pytest

from adsaffildb import tasks


class TestAugment(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_augment(self):
        self.assertEqual(1,2)
