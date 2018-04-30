import unittest

import scripts.classify_cause_area.feature_generation as feat


class GetDescriptionsWithoutStopwordsTest(unittest.TestCase):
    def setUp(self):
        self.descriptions_list = [
            "this is a sentence",
            "this is a sentence with punctuations !",
            "this is a sentence with lemmas cook cooking cooked"
        ]

    def test_should_generate_cleaned_descriptions(self):
        expected_result = [
            ["sentence"],
            ["sentence", "punctuations"],
            ["sentence", "lemmas", "cook", "cook", "cook"]
        ]
        result = feat.get_cleaned_descriptions(self.descriptions_list)

        self.assertCountEqual(result, expected_result)

    def test_should_generate_descriptions_with_stopwords(self):
        expected_result = [
            ["this", "be", "a", "sentence"],
            ["this", "be", "a", "sentence", "with", "punctuations"],
            ["this", "be", "a", "sentence", "with", "lemmas", "cook", "cook", "cook"]
        ]
        result = feat.get_cleaned_descriptions(self.descriptions_list, remove_stopwords=False)

        self.assertEqual(result, expected_result)

    def test_should_generate_descriptions_without_lemmatizing(self):
        expected_result = [
            ["sentence"],
            ["sentence", "punctuations"],
            ["sentence", "lemmas", "cook", "cooking", "cooked"]
        ]
        result = feat.get_cleaned_descriptions(self.descriptions_list, lemmatize_words=False)

        self.assertEqual(result, expected_result)

    def test_should_generate_descriptions_with_puctuations(self):
        expected_result = [
            ["sentence"],
            ["sentence", "punctuations", "!"],
            ["sentence", "lemmas", "cook", "cook", "cook"]
        ]
        result = feat.get_cleaned_descriptions(self.descriptions_list, remove_punctuations=False)

        self.assertEqual(result, expected_result)
