import unittest
import tagcounter.core as tagcounter

class TestTagCounter(unittest.TestCase):

    def test_get_put_synonyms(self):
        mydict = tagcounter.get_synonyms()
        urlPair = "aws: https://aws.amazon.com/".split(":", 1)
        mydict.update({urlPair[0]: urlPair[1]})
        tagcounter.put_sysnonyms(mydict)
        self.assertIsNotNone(tagcounter.get_synonyms().get(urlPair[0]))

    def test_get_tags_dictionary(self):
        mydict = tagcounter.get_tags_dictionary("<head><a><br><head><p>")
        self.assertEqual(mydict.get("head"), 2)
        self.assertEqual(mydict.get("a"), 1)
        self.assertEqual(mydict.get("br"), 1)
        self.assertEqual(mydict.get("p"), 1)