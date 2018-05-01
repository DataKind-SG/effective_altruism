from scripts.classify_cause_area.helpers \
    import get_cleaned_descriptions, get_sentence_from_list, \
    get_word_counts, get_distinct_words, read_from_csv

DATA_PATH = '../../data'

WEB_SCRAPE_CSV = DATA_PATH + '/output/web_scraping/web_scrape_v1_trunc.csv'
CAUSE_AREA_CSV = DATA_PATH + '/input/cause_area/cause_area.csv'

WEB_SCRAPE_PREPROCESSED_CSV = DATA_PATH + '/output/classify_cause_area/web_scrape_preprocessed.csv'
CAUSE_AREA_PREPROCESSED_CSV = DATA_PATH + '/output/classify_cause_area/cause_area_preprocessed.csv'

WEB_SCRAPE_DESCRIPTION_COLUMN_NAME = 'description'
CAUSE_AREA_KEYWORDS_COLUMN_NAME = 'Keywords'


class Preprocess:
    def start(self):
        web_scrape = read_from_csv(WEB_SCRAPE_CSV)
        web_scrape[WEB_SCRAPE_DESCRIPTION_COLUMN_NAME] \
            = web_scrape[WEB_SCRAPE_DESCRIPTION_COLUMN_NAME].fillna('')
        web_scrape = self.add_cleaned_text_field(web_scrape, WEB_SCRAPE_DESCRIPTION_COLUMN_NAME,
                                                 'description')

        web_scrape.to_csv(WEB_SCRAPE_PREPROCESSED_CSV, encoding='ISO-8859-1', index=False)

        cause_area = read_from_csv(CAUSE_AREA_CSV)
        cause_area[CAUSE_AREA_KEYWORDS_COLUMN_NAME] \
            = cause_area[CAUSE_AREA_KEYWORDS_COLUMN_NAME].fillna('')
        cause_area = self.add_cleaned_text_field(cause_area, CAUSE_AREA_KEYWORDS_COLUMN_NAME,
                                                 'keywords')

        cause_area.to_csv(CAUSE_AREA_PREPROCESSED_CSV, encoding='ISO-8859-1', index=False)

    @staticmethod
    def add_cleaned_text_field(df, data_column, new_column_prefix):
        keywords_cleaned = get_cleaned_descriptions(list(df[data_column]))
        keyword_counts = get_word_counts(keywords_cleaned)

        df[new_column_prefix + '_counts'] = keyword_counts
        df[new_column_prefix + '_cleaned'] = get_sentence_from_list(keywords_cleaned)
        df[new_column_prefix + '_cleaned_unique'] = get_distinct_words(keyword_counts)

        return df


Preprocess().start()
