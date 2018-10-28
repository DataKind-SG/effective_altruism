import pandas as pd
from gensim import corpora
from gensim.models import LdaModel

DATA_PATH = '../../data'
WEB_SCRAPE_PREPROCESSED = DATA_PATH + \
    '/output/classify_cause_area/web_scrape_preprocessed'

DESCRIPTION_COLUMN_NAME = 'description_cleaned'
LDA_SCORE_THRESHOLD = 0.01


class LdaAll:
    """
    """

    @staticmethod
    def do_lda(corpus, dictionary, topic_count):
        return LdaModel(
            corpus=corpus, id2word=dictionary,
            num_topics=topic_count, distributed=False,
        )

    def start(self):
        web_scrape_df = pd.read_pickle(WEB_SCRAPE_PREPROCESSED + ".pl")

        descriptions_cleaned = list(web_scrape_df[DESCRIPTION_COLUMN_NAME])

        descriptions_cleaned_splitted = descriptions_cleaned
        descriptions_cleaned_splitted = [
            d for d in descriptions_cleaned_splitted if len(d) > 0]
        descriptions_cleaned_splitted = [
            d.split(' ') for d in descriptions_cleaned_splitted]

        dictionary = corpora.Dictionary(descriptions_cleaned_splitted)
        corpus = [dictionary.doc2bow(text)
                  for text in descriptions_cleaned_splitted]

        experiment_topic_counts = [20]
        for topic_count in experiment_topic_counts:
            print('======== topic_count: ' + str(topic_count) + ' ========')

            lda = self.do_lda(corpus, dictionary, topic_count)

            lda_topics = lda.show_topics(
                num_topics=topic_count, num_words=100, formatted=False)
            self.print_filtered_lda_topics(lda_topics)

            print('================')

    @staticmethod
    def print_filtered_lda_topics(lda_topics):
        def filter_word_tuple(word, score):
            if not len(word) > 0:
                return False

            if score < LDA_SCORE_THRESHOLD:
                return False

            return True

        for topic, word_tuples_list in lda_topics:
            filtered_tuples = [(word, score)
                               for word, score in word_tuples_list
                               if filter_word_tuple(word, score)]

            words = [word for word, score in filtered_tuples]
            words_string = ",".join(words)

            words_with_scores = [
                str(score)[:4] + '*' + word for word, score in filtered_tuples]
            words_with_scores_string = ",".join(words_with_scores)

            print('id: ' + str(topic + 1))
            print('words: ' + words_string)
            print('words with weights: ' + words_with_scores_string)
            print('')


if __name__ == "__main__":
    LdaAll().start()
