import pandas as pd
import spacy

DATA_PATH = '../../data'
WEB_SCRAPE_CSV = DATA_PATH + '/output/web_scraping/web_scrape_v1.csv'
CAUSE_AREA_CSV = DATA_PATH + '/input/cause_area/cause_area.csv'


class CauseAreaClassifier:
    def __init__(self):
        pass

    def start(self):
        cause_area = self.read_cause_area()
        cause_area = self.add_stemmed_cause_area(cause_area)

        web_scrape = self.read_web_scrape()
        web_scrape = self.add_fields_to_web_scrape(web_scrape)
        pass

    def add_fields_to_web_scrape(self, df):
        def add_cleaned_org_description(df):
            clean_and_stemmed = self.generate_clean_and_stemmed(df["description"].values)

            df["description_cleaned"] = \
                pd.Series(clean_and_stemmed['descriptions']).values
            df["description_cleaned_tuple"] = \
                pd.Series(clean_and_stemmed['descriptions_tuple']).values

        add_cleaned_org_description(df)
        return df

    def read_web_scrape(self):
        return self.read_from_csv(WEB_SCRAPE_CSV)

    def add_stemmed_cause_area(self, cause_area_dict):
        def add_clean_and_stemmed(entry):
            return {
                'keywords_cleaned': entry['descriptions'],
                'keywords_cleaned_tuple': entry['descriptions_tuple']
            }

        clean_and_stemmed = self.generate_clean_and_stemmed([
            cause_area['keywords']
            for key, cause_area in cause_area_dict.items()
        ])

        cleaned_iter = iter(clean_and_stemmed['descriptions'])
        tuple_iter = iter(clean_and_stemmed['descriptions_tuple'])
        return {
            cause_area: {
                **value,
                'keywords_cleaned': next(cleaned_iter),
                'keywords_cleaned_tuple': next(tuple_iter),
            }
            for cause_area, value in cause_area_dict.items()
        }

    def read_cause_area(self):
        list_cause_areas = self.read_from_csv(CAUSE_AREA_CSV).to_dict(orient='records')

        def keywords_to_list(keywords_string):
            if type(keywords_string) is not str:
                return []

            keywords = keywords_string.strip().split(',')
            keywords_filtered = [keyword for keyword in keywords if len(keyword) != 0]
            return keywords_filtered

        cause_areas = {
            item["Causes/ Columns"]: {
                'keywords': item["Keywords"],
                'keywords_list': keywords_to_list(item["Keywords"])
            }
            for item in list_cause_areas
        }

        cause_areas_filtered = {
            cause_area: value
            for cause_area, value in cause_areas.items()
            if len(value['keywords_list']) != 0
        }

        return cause_areas_filtered

    @staticmethod
    def generate_clean_and_stemmed(list_docs):
        nlp = spacy.load('en', disable=['parser', 'tagger', 'ner'])

        lemmatized_descriptions = []
        lemmatized_keywords = []
        for doc in nlp.pipe(list_docs):
            important_words = [
                word.lemma_.lower() for word in doc
                if not word.is_stop and not word.is_punct
            ]

            lemmatized_keywords.append(tuple(important_words))

            sentence = " ".join(important_words)
            lemmatized_descriptions.append(sentence)

        return {
            'descriptions': lemmatized_descriptions,
            'descriptions_tuple': lemmatized_keywords
        }

    @staticmethod
    def read_from_csv(csv_path):
        return pd.read_csv(csv_path, encoding='ISO-8859-1')


CauseAreaClassifier().start()
