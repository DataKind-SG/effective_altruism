import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

DATA_PATH = '../../data'
WEB_SCRAPE_PREPROCESSED = DATA_PATH + '/output/classify_cause_area/web_scrape_preprocessed'

DESCRIPTION_COLUMN_NAME = 'description_cleaned'
N_TOP_TERMS = 100


class TfIdfAll:
    def start(self):
        web_scrape_df = pd.read_pickle(WEB_SCRAPE_PREPROCESSED + ".pl")

        descriptions = list(web_scrape_df[DESCRIPTION_COLUMN_NAME].dropna())

        count_vect = CountVectorizer()
        X_train_counts = count_vect.fit_transform(descriptions)

        tfidf_transformer = TfidfTransformer()
        X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

        top_terms = self.get_top_terms(count_vect, tfidf_transformer, N_TOP_TERMS)

        print('org descriptions: all - top ' + str(N_TOP_TERMS) + ' terms')
        print('================')
        for term in top_terms:
            print(term)

    @staticmethod
    def get_top_terms(count_vect, tfidf_transformer, n):
        indices = pd.np.argsort(tfidf_transformer.idf_)[::-1]
        features = count_vect.get_feature_names()
        top_features = [features[i] for i in indices[:n]]

        return top_features


TfIdfAll().start()
