from itertools import chain

import pandas as pd
import spacy

DATA_PATH = '../../data'
WEB_SCRAPE_PREPROCESSED = DATA_PATH + '/output/classify_cause_area/web_scrape_preprocessed'

CAUSE_AREAS_SCRAPED_COLUMN_NAME = 'cause_area'


class CauseAreasScraped:
    cause_area_unique_column_name = \
        CAUSE_AREAS_SCRAPED_COLUMN_NAME + '_unique'
    cause_area_unique_lemmatized_column_name = \
        CAUSE_AREAS_SCRAPED_COLUMN_NAME + '_unique_lemmatized'

    def start(self):
        web_scrape_df = pd.read_pickle(WEB_SCRAPE_PREPROCESSED + ".pl")

        web_scrape_df = self.add_unique_cause_areas_columns(web_scrape_df)

        all_cause_areas = web_scrape_df[self.cause_area_unique_column_name]
        all_cause_areas = list(chain.from_iterable(all_cause_areas))
        all_cause_areas = pd.Series(all_cause_areas)

        all_cause_areas_lemmatized = web_scrape_df[self.cause_area_unique_lemmatized_column_name]
        all_cause_areas_lemmatized = list(chain.from_iterable(all_cause_areas_lemmatized))
        all_cause_areas_lemmatized = pd.Series(all_cause_areas_lemmatized)

        total_cause_area_count = all_cause_areas.size

        cause_area_counts_df = pd.DataFrame(all_cause_areas.value_counts().reset_index())
        cause_area_counts_df.columns = ['cause area', 'count']
        cause_area_counts_df['percentage'] = \
            cause_area_counts_df['count'].apply(lambda count: count / total_cause_area_count)

        print("Total organizations with cause areas: " + str(all_cause_areas.size))
        print("Total unique cause areas: " + str(all_cause_areas.unique().size))
        print('Total unique lemmatized cause areas: '
              + str(all_cause_areas_lemmatized.unique().size))

        cause_areas_merged_by_lemmatization = \
            set.difference(set(all_cause_areas), set(all_cause_areas_lemmatized))
        print('( number of cause areas changed by lemmatization: '
              + str(len(cause_areas_merged_by_lemmatization)) + ' )')

        print("=== Cause Areas ===")
        pd.set_option('display.max_colwidth', 50)
        pd.set_option('display.max_rows', None)
        print(cause_area_counts_df)

    def add_unique_cause_areas_columns(self, df):
        df[CAUSE_AREAS_SCRAPED_COLUMN_NAME] = \
            df[CAUSE_AREAS_SCRAPED_COLUMN_NAME].fillna("")
        df[CAUSE_AREAS_SCRAPED_COLUMN_NAME] = \
            df[CAUSE_AREAS_SCRAPED_COLUMN_NAME].astype(str)

        df[self.cause_area_unique_column_name] = \
            self.generate_unique_cause_area_set(df, CAUSE_AREAS_SCRAPED_COLUMN_NAME)
        df[self.cause_area_unique_lemmatized_column_name] = \
            self.generate_unique_cause_area_lemmatized(df, self.cause_area_unique_column_name)

        return df

    @staticmethod
    def generate_unique_cause_area_set(web_scrape_df, cause_area_column_name):
        def generate_set(cause_area_string):
            if cause_area_string is None or len(cause_area_string) == 0:
                return set()

            cause_areas_splitted = cause_area_string.lower()
            cause_areas_splitted = cause_areas_splitted.split(",")
            cause_areas_splitted = [c.strip() for c in cause_areas_splitted
                                    if len(c) > 0]

            return set(cause_areas_splitted)

        return web_scrape_df[cause_area_column_name].apply(generate_set)

    @staticmethod
    def generate_unique_cause_area_lemmatized(web_scrape_df, cause_area_unique_column_name):
        nlp = spacy.load('en', disable=['parser', 'tagger', 'ner'])

        def generate_lemmatized_set(cause_area_set):
            lemmatized_set = set()

            for cause_area in cause_area_set:
                doc = nlp(cause_area)

                cause_area_lemmatized = [token.lemma_ for token in doc]
                cause_area_lemmatized = ' '.join(cause_area_lemmatized)
                lemmatized_set.add(cause_area_lemmatized)

            return lemmatized_set

        return web_scrape_df[cause_area_unique_column_name].apply(generate_lemmatized_set)


CauseAreasScraped().start()
