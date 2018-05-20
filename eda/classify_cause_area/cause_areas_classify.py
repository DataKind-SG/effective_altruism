import math

import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

import eda.classify_cause_area.cause_areas_scraped as cas

DATA_PATH = '../../data'
WEB_SCRAPE_PREPROCESSED = DATA_PATH + '/output/classify_cause_area/web_scrape_preprocessed'

CAUSE_AREAS_INVESTIGATED = {'education', 'children', 'religious', 'health', 'environment'}

TEST_SIZE = 0.1


class CauseAreasClassify:
    def start(self):
        df = pd.read_pickle(WEB_SCRAPE_PREPROCESSED + ".pl")

        # add set() helpers for cause areas
        df = cas.CauseAreasScraped().add_unique_cause_areas_columns(df)

        # create features and helper columns
        mlb = MultiLabelBinarizer()
        df = self.add_cause_area_classifier_labels(df, CAUSE_AREAS_INVESTIGATED, mlb)
        df = self.add_investigated_cause_areas_summary(df, CAUSE_AREAS_INVESTIGATED)
        df = self.add_investigated_cause_columns(df, CAUSE_AREAS_INVESTIGATED)
        df = self.add_investigated_cause_counts(df, 'clf_labels')

        orgs_with_more_than_one_investigated_cause_area = \
            len(df[df['investigated_cause_areas_count'] > 1])
        print('orgs with more than one investigated cause area: '
              + str(orgs_with_more_than_one_investigated_cause_area))

        # remove orgs that do not fall in investigated cause areas
        df = df[df['investigated_cause_areas_count'] > 0]

        print("orgs with at least one investigated cause area: " + str(len(df)))

        # stratify data by cause areas
        df = self.do_train_test_stratify(df, CAUSE_AREAS_INVESTIGATED)

        # TODO
        # train tf idf and store features
        # test tf idf and store features (do not fit, only transform)
        # put into classifier

    @staticmethod
    def add_cause_area_classifier_labels(df, cause_areas, mlb):
        intersected_cause_areas = df['cause_area_unique'] \
            .apply(lambda causes: set.intersection(causes, cause_areas))
        df['clf_labels'] = list(mlb.fit_transform(intersected_cause_areas))

        return df

    @staticmethod
    def add_investigated_cause_areas_summary(df, cause_areas):
        df['investigated_cause_areas_summary'] = df['cause_area_unique'] \
            .apply(lambda causes: set.intersection(causes, cause_areas))

        return df

    @staticmethod
    def add_investigated_cause_columns(df, cause_areas):
        cause_area_prefix = "ca_"

        for cause_area in cause_areas:
            cause_area_column = cause_area_prefix + cause_area
            df[cause_area_column] = df['cause_area_unique'] \
                .apply(lambda causes: True if cause_area in causes else False)

        return df

    @staticmethod
    def add_investigated_cause_counts(df, labels_column_name):
        df['investigated_cause_areas_count'] = df[labels_column_name] \
            .apply(lambda l: sum(l))

        return df

    @staticmethod
    def do_train_test_stratify(df, cause_areas, random_state=1):
        cause_area_prefix = "ca_"

        df['is_train'] = False

        for cause_area in cause_areas:
            cause_area_column = cause_area_prefix + cause_area
            cause_area_rows = df[df[cause_area_column]]

            rows_count = len(cause_area_rows)
            train_rows_count = math.floor(rows_count * TEST_SIZE)

            train_rows = cause_area_rows.sample(n=train_rows_count, random_state=random_state)
            train_rows_index = train_rows.index.values

            df.loc[train_rows_index, 'is_train'] = True

        return df


if __name__ == "__main__":
    CauseAreasClassify().start()
