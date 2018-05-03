import pandas as pd

DATA_PATH = '../../data'
WEB_SCRAPE_PREPROCESSED = DATA_PATH + '/output/classify_cause_area/web_scrape_preprocessed'

CAUSE_AREAS_SCRAPED_COLUMN_NAME = 'cause_area'


class CauseAreasScraped:
    def start(self):
        web_scrape_df = pd.read_pickle(WEB_SCRAPE_PREPROCESSED + ".pl")

        cause_areas = list(web_scrape_df[CAUSE_AREAS_SCRAPED_COLUMN_NAME].dropna())
        cause_areas = [c for c in cause_areas if len(c) > 0]
        cause_areas = self.split_cause_areas(cause_areas)

        cause_areas_unique = set(cause_areas)
        cause_areas_series = pd.Series(cause_areas)

        print("Total cause_area entries: " + str(len(cause_areas)))
        print("Unique entries: " + str(len(cause_areas_unique)))

        print("=== Cause Areas ===")
        print(cause_areas_series.value_counts())

    @staticmethod
    def split_cause_areas(cause_areas_list):
        cause_areas_splitted = []

        for cause_areas in cause_areas_list:
            cause_areas_splitted_unclean = cause_areas.split(",")
            cause_areas_splitted_unclean = [c.strip() for c in cause_areas_splitted_unclean
                                            if len(c) > 0]

            cause_areas_splitted = cause_areas_splitted + cause_areas_splitted_unclean

        return cause_areas_splitted


CauseAreasScraped().start()
