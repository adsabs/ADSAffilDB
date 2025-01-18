import unittest

import pytest

from adsaffildb import normalize


class TestNormalize(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_basicstring(self):
        str1 = "UnIvErSiTy of california, berkeley"
        str1out = "UNIVERSITYOFCALIFORNIABERKELEY"
        teststr = normalize.normalize_string(str1, kill_spaces=True, upper_case=True)
        self.assertEqual(teststr, str1out)

        str2 = "Center for Astrophysics | Harvard & Smithsonian, 60 Garden St., Cambridge, MA 02138"
        str2out = "CENTERFORASTROPHYSICSHARVARD&SMITHSONIAN60GARDENSTCAMBRIDGEMA02138"
        teststr = normalize.normalize_string(str2, kill_spaces=True, upper_case=True)
        self.assertEqual(teststr, str2out)
