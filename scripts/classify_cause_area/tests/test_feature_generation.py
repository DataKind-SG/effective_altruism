import unittest
import unittest.mock as mock

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

        self.assertEqual(result, expected_result)

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


class GetWordCounts(unittest.TestCase):
    def setUp(self):
        self.descriptions_list = [
            ["this", "is", "a", "sentence"],
            ["this", "is", "a", "sentence", "with", "many", "this", "this"]
        ]

    def test_should_generate_word_counts(self):
        expected_result = [
            {"this": 1, "is": 1, "a": 1, "sentence": 1},
            {"this": 3, "is": 1, "a": 1, "sentence": 1, "with": 1, "many": 1},
        ]
        result = feat.get_word_counts(self.descriptions_list)

        self.assertEqual(result, expected_result)


class ReadFromCSVTest(unittest.TestCase):
    @mock.patch('scripts.classify_cause_area.feature_generation.pd')
    def test_should_read_from_csv(self, mock_pandas):
        feat.read_from_csv('some-csv-path')

        mock_pandas.read_csv.assert_called_with('some-csv-path', encoding='ISO-8859-1')

    @mock.patch('scripts.classify_cause_area.feature_generation.pd')
    def test_should_read_from_csv_with_set_encoding(self, mock_pandas):
        feat.read_from_csv('some-csv-path', encoding='UTF-8')

        mock_pandas.read_csv.assert_called_with('some-csv-path', encoding='UTF-8')
