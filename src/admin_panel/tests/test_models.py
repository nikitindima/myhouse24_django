from django.db import IntegrityError
from django.test import TestCase

from src.admin_panel.models import Measure


class MeasureTestCase(TestCase):
    def setUp(self):
        Measure.objects.create(name="метры")
        Measure.objects.create(name="")

    def test_measure_return_name(self):
        """Measures return their names"""
        measure1 = Measure.objects.get(name="метры")
        measure2 = Measure.objects.get(name="")
        self.assertEqual('метры', str(measure1))
        self.assertEqual('', str(measure2))
