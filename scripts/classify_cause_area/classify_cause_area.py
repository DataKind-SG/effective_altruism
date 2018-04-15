import pandas as pd
import spacy

DATA_PATH = '../../data'
WEB_SCRAPE_CSV = DATA_PATH + '/output/web_scraping/web_scrape_v1.csv'
CAUSE_AREA_CSV = DATA_PATH + '/input/cause_area/cause_area.csv'
WEB_SCRAPE_IMPUTED_CAUSE_AREAS_CSV \
    = DATA_PATH + '/output/classify_cause_area/web_scrape_imputed_cause_areas.csv'


class CauseAreaClassifier:
    def __init__(self):
        pass

    def start(self):
        cause_area = self.read_cause_area()
        cause_area = self.add_stemmed_cause_area(cause_area)

        web_scrape = self.read_web_scrape()
        web_scrape = self.add_fields_to_web_scrape(web_scrape)

        web_scrape = self.score_based_on_cause_area(web_scrape, cause_area)
        web_scrape = self.add_number_of_cause_areas_per_organization(web_scrape, cause_area)

        web_scrape.to_csv(WEB_SCRAPE_IMPUTED_CAUSE_AREAS_CSV)

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

    def add_stemmed_cause_area(self, cause_area_dict):
        clean_and_stemmed = self.generate_clean_and_stemmed([
            cause_area['keywords']
            for key, cause_area in cause_area_dict.items()
        ])

        cleaned_iter = iter(clean_and_stemmed['descriptions'])
        set_iter = iter(clean_and_stemmed['descriptions_set'])
        return {
            cause_area: {
                **value,
                'keywords_cleaned': next(cleaned_iter),
                'keywords_cleaned_set': next(set_iter),
            }
            for cause_area, value in cause_area_dict.items()
        }

    def read_web_scrape(self):
        return self.read_from_csv(WEB_SCRAPE_CSV)

    def add_fields_to_web_scrape(self, df):
        def add_cleaned_org_description():
            clean_and_stemmed = self.generate_clean_and_stemmed(df["description"].fillna("").values)

            df["description_cleaned"] = \
                pd.Series(clean_and_stemmed['descriptions']).values
            df["description_cleaned_set"] = \
                pd.Series(clean_and_stemmed['descriptions_set']).values

        add_cleaned_org_description()
        return df

    @staticmethod
    def score_based_on_cause_area(df, cause_area):
        cause_area_names = list(cause_area.keys())

        def add_cause_area_columns():
            for cause_name in cause_area_names:
                df['cause_area_' + cause_name] = 0

        add_cause_area_columns()

        def score_organizations_by_cause_area(organization_descriptions, cause_area_keywords_set):
            counters = [
                len(set.intersection(description_set, cause_area_keywords_set))
                for description_set in organization_descriptions
            ]

            return pd.Series(counters).values

        def do_scoring():
            for cause_area_name, value in cause_area.items():
                keywords_set = value['keywords_cleaned_set']
                df['cause_area_' + cause_area_name] = score_organizations_by_cause_area(
                    df['description_cleaned_set'], keywords_set)

        do_scoring()

        return df

    @staticmethod
    def add_number_of_cause_areas_per_organization(df, cause_area_dict):
        df['cause_area_count'] = 0

        for cause_area_name in cause_area_dict.keys():
            column_name = 'cause_area_' + cause_area_name

            specific_cause_area_count = df[column_name]
            specific_cause_area_count = (specific_cause_area_count > 0).astype(int)

            df['cause_area_count'] = df['cause_area_count'] + specific_cause_area_count

        return df

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

            lemmatized_keywords.append(set(important_words))

            sentence = " ".join(important_words)
            lemmatized_descriptions.append(sentence)

        return {
            'descriptions': lemmatized_descriptions,
            'descriptions_set': lemmatized_keywords
        }

    @staticmethod
    def read_from_csv(csv_path):
        return pd.read_csv(csv_path, encoding='ISO-8859-1')


CauseAreaClassifier().start()
