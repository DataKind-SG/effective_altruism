import pandas as pd

from scripts.classify_cause_area.helpers import add_columns_to_df, \
    remove_rows_with_null_or_empty

DATA_PATH = '../../../../data'

WEB_SCRAPE_PREPROCESSED = DATA_PATH + '/output/classify_cause_area/web_scrape_preprocessed'
CAUSE_AREA_PREPROCESSED = DATA_PATH + '/output/classify_cause_area/cause_area_preprocessed'

WEB_SCRAPE_IMPUTED_CAUSE_AREAS \
    = DATA_PATH + '/output/classify_cause_area/web_scrape_imputed_cause_areas'

CAUSE_AREAS_COLUMN_NAME = 'Causes/ Columns'


class KeywordCounts:
    def start(self):
        cause_area_df = pd.read_pickle(CAUSE_AREA_PREPROCESSED + ".pl")
        web_scrape_df = pd.read_pickle(WEB_SCRAPE_PREPROCESSED + ".pl")

        # clean descriptions
        orgs_all_count = len(web_scrape_df)
        web_scrape_df = remove_rows_with_null_or_empty(web_scrape_df, 'description')

        # print number of removed orgs
        orgs_with_description = len(web_scrape_df)
        orgs_with_empty_description = orgs_all_count - orgs_with_description
        print('info: removed ' + str(orgs_with_empty_description) + ' orgs with empty description')

        # add cause_area
        cause_areas = list(cause_area_df['Causes/ Columns'].dropna())
        web_scrape_df = add_columns_to_df(web_scrape_df, cause_areas, 'ca_', 0)

        # do scoring
        web_scrape_df = self.score_by_keyword_count(web_scrape_df, cause_area_df)

        # add summary fields
        web_scrape_df = self.add_number_of_cause_areas_per_organization(web_scrape_df, cause_areas)
        web_scrape_df = self.add_cause_areas_per_organization(web_scrape_df, cause_areas)

        # save to csv
        web_scrape_df.to_csv(WEB_SCRAPE_IMPUTED_CAUSE_AREAS + ".csv", index=False)
        web_scrape_df.to_pickle(WEB_SCRAPE_IMPUTED_CAUSE_AREAS + ".pl")

    @staticmethod
    def score_by_keyword_count(web_scrape_df, cause_areas_df):
        def calcuate_score_from_counts_and_keywords_overlap(word_dict, keywords):
            score = 0
            for keyword in keywords:
                if keyword not in word_dict:
                    continue
                score = score + word_dict[keyword]

            return score

        def compute_org_score_by_cause_area(description_counts, cause_area_keywords_set):
            counters = [
                calcuate_score_from_counts_and_keywords_overlap(word_counts_dict,
                                                                cause_area_keywords_set)
                for word_counts_dict in description_counts
            ]

            return pd.Series(counters).values

        cause_area_attr = '_' + str(cause_areas_df.columns.get_loc(CAUSE_AREAS_COLUMN_NAME) + 1)

        for cause_area in cause_areas_df.itertuples():
            cause_area_name = getattr(cause_area, cause_area_attr)
            keywords_set = cause_area.keywords_cleaned_unique

            cause_area_scores = compute_org_score_by_cause_area(
                web_scrape_df['description_counts'],
                keywords_set)
            web_scrape_df['ca_' + cause_area_name] = cause_area_scores

        return web_scrape_df

    @staticmethod
    def add_number_of_cause_areas_per_organization(df, cause_areas_list):
        df['cause_area_count'] = 0

        for cause_area_name in cause_areas_list:
            column_name = 'ca_' + cause_area_name

            specific_cause_area_count = df[column_name]
            specific_cause_area_count = (specific_cause_area_count > 0).astype(int)

            df['cause_area_count'] = df['cause_area_count'] + specific_cause_area_count

        return df

    @staticmethod
    def add_cause_areas_per_organization(df, cause_areas_list):
        df['cause_areas_imputed'] = ''

        for cause_area_name in cause_areas_list:
            column_name = 'ca_' + cause_area_name

            matched_rows = df[column_name]
            matched_rows = matched_rows.apply(lambda x: cause_area_name + ', ' if x > 0 else "")

            df['cause_areas_imputed'] = df['cause_areas_imputed'] + matched_rows

        return df


if __name__ == "__main__":
    KeywordCounts().start()
