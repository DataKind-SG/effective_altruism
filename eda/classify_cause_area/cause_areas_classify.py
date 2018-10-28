import math

import pandas as pd
from sklearn import ensemble
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MultiLabelBinarizer

import eda.classify_cause_area.cause_areas_scraped as cas

DATA_PATH = '../../data'
WEB_SCRAPE_PREPROCESSED = DATA_PATH + \
    '/output/classify_cause_area/web_scrape_preprocessed'

CAUSE_AREAS_INVESTIGATED = {'education',
                            'children', 'religious', 'health', 'environment'}

TEST_SIZE = 0.1


class CauseAreasClassify:
    def start(self):
        df = pd.read_pickle(WEB_SCRAPE_PREPROCESSED + ".pl")

        # remove orgs with like-empty descriptions
        df = self.remove_orgs_with_empty_descriptions(df)

        # add set() helpers for cause areas
        df = cas.CauseAreasScraped().add_unique_cause_areas_columns(df)

        # create features and helper columns
        mlb = MultiLabelBinarizer()
        df = self.add_cause_area_classifier_labels(
            df, CAUSE_AREAS_INVESTIGATED, mlb)
        df = self.add_investigated_cause_areas_summary(
            df, CAUSE_AREAS_INVESTIGATED)
        df = self.add_investigated_cause_columns(df, CAUSE_AREAS_INVESTIGATED)
        df = self.add_investigated_cause_counts(df, 'clf_labels')

        orgs_with_more_than_one_investigated_cause_area = \
            len(df[df['investigated_cause_areas_count'] > 1])
        print('orgs with more than one investigated cause area: '
              + str(orgs_with_more_than_one_investigated_cause_area))

        # remove orgs that do not fall in investigated cause areas
        df = df[df['investigated_cause_areas_count'] > 0]
        print("orgs with at least one investigated cause area: "
              + str(len(df)))

        # stratify data by cause areas
        df = self.do_train_test_stratify(df, CAUSE_AREAS_INVESTIGATED)

        # generate tf-idf features
        tf_idf_vectorizer = TfidfVectorizer(max_features=100)
        df = self.generate_tf_idf_features(df, tf_idf_vectorizer)

        # setup test/train
        train_rows = df[~df['is_test']]
        x_train = list(train_rows['tf_idf_feature'])
        y_train = list(train_rows['clf_labels'])

        test_rows = df[df['is_test']]
        x_test = list(test_rows['tf_idf_feature'])
        y_test = list(test_rows['clf_labels'])

        # classify
        clf = ensemble.RandomForestClassifier(n_jobs=-1)
        clf = clf.fit(x_train, y_train)
        test_predict = clf.predict(x_test)

        # print results
        print('\n- Train/Test counts -')
        for cause_area in CAUSE_AREAS_INVESTIGATED:
            cause_area_prefix = 'ca_'
            cause_area_column = cause_area_prefix + cause_area
            cause_area_rows = df[df[cause_area_column]]

            total = len(cause_area_rows)
            train = len(cause_area_rows[~cause_area_rows['is_test']])
            test = total - train

            print(cause_area + ": " + str(train) + "/" + str(test))

        print('\n- Accuracy -')
        predicted_classes = list(mlb.classes_)
        for cause_area in CAUSE_AREAS_INVESTIGATED:
            index = predicted_classes.index(cause_area)
            accuracy = accuracy_score(
                [a[index] for a in y_test],
                [a[index] for a in test_predict]
            )
            print(cause_area + ": " + str(accuracy))

    @staticmethod
    def remove_orgs_with_empty_descriptions(df):
        def has_empty_description(text):
            if text is None:
                return True

            stripped_text = text.strip()
            if len(stripped_text) == 0:
                return True

            return False

        rows_empty_descriptions = df['description_cleaned'] \
            .apply(has_empty_description) \
            .apply(lambda v: True if v is True else None) \
            .dropna()

        return df.loc[~df.index.isin(rows_empty_descriptions.index.values)]

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

        df['is_test'] = False

        for cause_area in cause_areas:
            cause_area_column = cause_area_prefix + cause_area
            cause_area_rows = df[df[cause_area_column]]

            rows_count = len(cause_area_rows)
            train_rows_count = math.floor(rows_count * TEST_SIZE)

            test_rows = cause_area_rows.sample(
                n=train_rows_count, random_state=random_state)
            test_rows_index = test_rows.index.values

            df.loc[test_rows_index, 'is_test'] = True

        return df

    @staticmethod
    def generate_tf_idf_features(df, tf_idf_vectorizer):
        df['tf_idf_feature'] = None
        df['tf_idf_feature'] = df['tf_idf_feature'].astype(object)

        train_rows = df[~df['is_test']]
        x_train = tf_idf_vectorizer.fit_transform(
            train_rows['description_cleaned'])
        for df_index, feature_vector in zip(train_rows.index.values,
                                            x_train.toarray().tolist()):
            df.at[df_index, 'tf_idf_feature'] = feature_vector

        test_rows = df[df['is_test']]
        x_test = tf_idf_vectorizer.transform(test_rows['description_cleaned'])
        for df_index, feature_vector in zip(test_rows.index.values,
                                            x_test.toarray().tolist()):
            df.at[df_index, 'tf_idf_feature'] = feature_vector

        return df


if __name__ == "__main__":
    CauseAreasClassify().start()
