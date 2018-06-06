import pandas as pd
import spacy


def get_cleaned_descriptions(descriptions_list, remove_stopwords=True,
                             remove_punctuations=True, lemmatize_words=True):
    cleaned_descriptions = []
    nlp = spacy.load('en', disable=['parser', 'tagger', 'ner'])

    def do_word_filter(word):
        if remove_stopwords and word.is_stop:
            return False
        if remove_punctuations and word.is_punct:
            return False
        return True

    for doc in nlp.pipe(descriptions_list):
        important_words = [
            word.lemma_.lower() if lemmatize_words else word.text.lower()
            for word in doc
            if do_word_filter(word)
        ]

        cleaned_descriptions.append(important_words)

    return cleaned_descriptions


def get_word_counts(descriptions_list):
    def do_word_count(word_list):
        word_count_dict = {}

        for word in word_list:
            if word not in word_count_dict:
                word_count_dict[word] = 1
                continue
            word_count_dict[word] = word_count_dict[word] + 1

        return word_count_dict

    return [do_word_count(word_list) for word_list in descriptions_list]


def read_from_csv(csv_path, encoding='ISO-8859-1'):
    return pd.read_csv(csv_path, encoding=encoding)


def get_distinct_words(word_counts_list):
    return [set(word_counts_dict.keys()) for word_counts_dict in word_counts_list]


def get_sentence_from_list(list_of_list_of_words):
    return [' '.join(list_of_words) for list_of_words in list_of_list_of_words]


def add_columns_to_df(df, column_names_list, new_columns_prefix, default_value):
    for column_name in column_names_list:
        df[new_columns_prefix + column_name] = default_value

    return df


def remove_rows_with_null_or_empty(df, column_name):
    df[column_name] = df[column_name].replace('', pd.np.nan)
    df = df[pd.notnull(df[column_name])]

    return df
