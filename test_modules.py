import unittest
from text_preprocessor import Preprocessor

class TestMethods(unittest.TestCase):

    def test_preprocessor(self):
        preprocessor=Preprocessor()
        self.assertEqual(preprocessor.counter, 6)
        self.assertEqual(preprocessor.lemmatize_sentence("what is your name"), "name")

if __name__ == '__main__':
    unittest.main()