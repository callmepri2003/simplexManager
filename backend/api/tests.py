from django.test import TestCase

# Create your tests here.

class ApiTestCase(TestCase):
  def setup(self):
    None
  
  def testTest(self):
    self.assertEqual(True, True)