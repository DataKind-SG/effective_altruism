#!/usr/bin/env python
# coding: utf-8

# # EA x DKSG
# **classification: web scrape**
# 
# classify organizations into cause areas based on descriptions
# - basically, descriptions -> cause areas
# 
# ## methodology
# - clean up organization descriptions
#     - drop stopwords
#     - drop punctuations
#     - lemmatize words
# - create count vectors for each description
# - use count vectors as feature for classification with
#     - decision trees
#     - random forest regressor
#     
# ## hypothesis
# an organization with certain keywords in its description should be involved in a cause area if the keywords match up with the keywords defined in the cause area
# 
# ## clean up organization descriptions

# In[13]:


## setup
import pandas as pd
get_ipython().run_line_magic('run', 'setup/env_setup.py')
get_ipython().run_line_magic('run', '../common/filepaths.py')
get_ipython().run_line_magic('run', '../common/helpers.py')


# In[14]:


web_df = read_from_csv(WEB_SCRAPE_CSV)
web_df.head()


# In[15]:


## fill up empty descriptions
web_df['description'] = web_df['description'].fillna('')

## add cleaned description
web_df['desc_clean_words'] = get_cleaned_descriptions(list(web_df['description']), True, True, True)
web_df['desc_clean'] = get_sentence_from_list(list(web_df['desc_clean_words']))


# Q: number/proportion of organizations with descriptions

# In[16]:


orgs_with_description_index = web_df['description'].apply(lambda d: None if d == '' else d).dropna().index

number_of_orgs_with_description = len(orgs_with_description_index)
number_of_orgs_with_description

print("Number of organizations with descriptions: %d" % number_of_orgs_with_description)
print("% of organizations with descriptions: "+ str(number_of_orgs_with_description/len(web_df)))


# ## clean up cause areas

# In[17]:


import re

## add cleaned cause areas
def clean_cause_area(cause_area_raw):
    sentence = cause_area_raw
    sentence = re.sub(r'(&)|(and)',',',sentence)
    sentence = re.sub(r'[()1-9]+',' ',sentence)
    sentence = sentence.replace("."," ").replace("-"," ")
    sentence = sentence.replace("\\",",").replace("/",",")
    sentence = re.sub(r'[^a-zA-Z0-9,]',' ', sentence)
    
    def remove_single_char_word_in_cause_area(cause_area):
        w = cause_area.split(" ")
        w = [w for w in w if len(w) > 1]
        return " ".join(w)
    
    words = sentence.lower().split(",")
    words = [w.strip() for w in words]
    words = [re.sub(r'[ ]{2,}',' ', w) for w in words]
    words = [remove_single_char_word_in_cause_area(w) for w in words]
    words = [w for w in words if len(w) > 0]
    return set(words)

web_df['cause_area'] = web_df['cause_area'].fillna('')
web_df['cause_area_clean'] = web_df['cause_area'].apply(clean_cause_area)
web_df['cause_area_count'] = web_df['cause_area_clean'].apply(lambda l: len(l))


# view existing cause areas

# In[18]:


web_df[['desc_clean_words', 'desc_clean', 'cause_area_clean', 'cause_area_count']].head()


# ## basic viz

# In[19]:


get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('run', 'setup/viz_setup.py')


# #### cause areas (web scraped)

# In[20]:


from itertools import chain
def get_web_cause_area_summary(web_df):
    df = list(chain.from_iterable(list(web_df['cause_area_clean'].apply(lambda s: list(s)))))
    df = pd.Series(df) 
    df = pd.DataFrame(df.value_counts().reset_index())
    df.columns = ['cause area', 'count']
    
    total_cause_area_count = sum(df['count'])
    df['%'] = df['count'].apply(lambda count: count/total_cause_area_count)
    
    return df

web_cause_area_df = get_web_cause_area_summary(web_df)


# In[21]:


print("Number of unique cause areas: %d" % len(web_cause_area_df))


# Q: top 20 cause areas with highest counts

# In[22]:


web_cause_area_df[:20]


# Q: cause area by counts bar chart (all)

# In[23]:


plt = web_cause_area_df.plot.bar(x='cause area', y='count')
plt.xaxis.set_visible(False)


# Q: cause area by counts bar chart (top 20)

# In[24]:


plt = web_cause_area_df[:20].plot.bar(x='cause area', y='count')
plt


# #### distribution of number of organizations to cause area counts

# In[25]:


cause_area_count_distribution = pd.DataFrame(web_df['cause_area_count'].value_counts().reset_index())
cause_area_count_distribution.columns = ['number of cause areas','number of organizations']

print(cause_area_count_distribution)
cause_area_count_distribution['number of organizations'].plot.bar()


# #### cause areas (web scraped) for organizations with non-empty descriptions
# - it is meaningless to train a classifier with observations with empty descriptions

# In[26]:


web_cause_area_nonempty_df = get_web_cause_area_summary(web_df[web_df['desc_clean'] != ''])

print("- After Filtering out organizations with empty descriptions -")
print("number of unique cause areas: %d" % len(web_cause_area_nonempty_df))
web_cause_area_nonempty_df[:20]


# ## create features: count vectors for each description
# - take top web_cause_areas by count

# In[27]:


## ml setup
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn import tree
from sklearn import ensemble
from sklearn.metrics import accuracy_score


# #### select top cause areas (web scrape)
# n = 50

# In[28]:


web_cause_area_select = web_cause_area_nonempty_df[:50]


# Q: proportion of top web cause areas (against all counts)

# In[29]:


sum(web_cause_area_select['%'])


# create cause_area_clean_filter (ie. a copy of cause_area_clean with only filtered matches)

# In[30]:


web_df['cause_area_clean_filter'] =     web_df['cause_area_clean'].apply(lambda c: c.intersection(set(web_cause_area_select['cause area'])))


# #### select orgs in selected cause areas
# select orgs that are within selected cause areas, and do not have empty descriptions

# In[31]:


def select_orgs_in_cause_area(df):
    orgs_with_non_empty_descriptions = df['desc_clean']         .apply(lambda desc: None if desc == '' else desc)         .dropna()         .index
    
    orgs_with_at_least_one_cause_area = df.iloc[orgs_with_non_empty_descriptions]         ['cause_area_clean_filter']         .apply(lambda c: len(c) if len(c) > 0 else None)         .dropna()         .index
    
    return df.iloc[orgs_with_at_least_one_cause_area]

web_df_select = select_orgs_in_cause_area(web_df)
web_df_select.head()


# Q: total number of organizations after filtering

# In[32]:


len(web_df_select)


# #### split train/test/validation

# In[33]:


train_ratio, test_ratio, validation_ratio_from_test = (0.7,0.3,0.5)


# In[34]:


def do_train_test_validation_split(df, train_ratio, test_ratio, validation_ratio_from_test, random_state=None):
    train_data, test_data =         train_test_split(df, train_size=train_ratio, test_size=test_ratio, random_state=random_state)
    validation_data, test_data =         train_test_split(test_data, train_size=validation_ratio_from_test, 
                          test_size=1-validation_ratio_from_test, random_state=random_state)
            
    return train_data, test_data, validation_data
    
train_data, test_data, validation_data =     do_train_test_validation_split(web_df_select, train_ratio, test_ratio, validation_ratio_from_test, 1)


# train/test/validation counts

# In[35]:


print("train count: %d" % len(train_data))
print("test count: %d" % len(test_data))
print("validation count: %d" % len(validation_data))


# train/test/validation counts by cause area
# 
# - to check that each cause area is represented in test/train/validation

# In[36]:


def generate_data_split_cause_area_counts(train_data, test_data, validation_data, cause_areas):
    def get_number_of_orgs_that_match_cause_area(df, cause_area):
        return df['cause_area_clean_filter']             .apply(lambda causes: causes if cause_area in causes else None)             .dropna()             .count()
    
    split_counts = []
    for cause_area in cause_areas:
        split_counts.append({
            'cause area': cause_area,
            'train': get_number_of_orgs_that_match_cause_area(train_data, cause_area),
            'test': get_number_of_orgs_that_match_cause_area(test_data, cause_area),
            'validation': get_number_of_orgs_that_match_cause_area(validation_data, cause_area),
        })
    
    return split_counts

split_data_cause_area_counts = pd.DataFrame(
    generate_data_split_cause_area_counts(train_data, test_data, validation_data, set(web_cause_area_select['cause area']))
)
split_data_cause_area_counts


# Q: are all cause areas represented in all of the data sets? (ie. no 0 counts in any of the cause areas)

# In[37]:


def get_zero_counts_cause_areas_from_datasets(df):
    return df.query('test == 0 | train == 0 | validation == 0')
    
zero_counts_cause_areas = get_zero_counts_cause_areas_from_datasets(split_data_cause_area_counts)
len(zero_counts_cause_areas) > 0


# #### encode org descriptions using CountVectorizer

# In[38]:


count_vectorizer = CountVectorizer(max_features=100, decode_error='ignore')

train_data_feat = count_vectorizer.fit_transform(train_data['desc_clean'])
test_data_feat = count_vectorizer.transform(test_data['desc_clean'])
validation_data_feat = count_vectorizer.transform(validation_data['desc_clean'])


# ## create labels: cause area categories
# #### encode cause area categories to multi-label

# In[39]:


mlb = MultiLabelBinarizer()
mlb.fit([web_cause_area_select['cause area']])
mlb.classes_


# In[40]:


validation_data.head()


# In[41]:


train_data_label = mlb.transform(train_data['cause_area_clean_filter'])
test_data_label = mlb.transform(test_data['cause_area_clean_filter'])
validation_data_label = mlb.transform(validation_data['cause_area_clean_filter'])


# ## classify orgs

# In[42]:


base_clf = ensemble.RandomForestClassifier(n_estimators=25, n_jobs=-1)
base_clf = base_clf.fit(train_data_feat, train_data_label)

test_predict = base_clf.predict(test_data_feat)
train_predict = base_clf.predict(train_data_feat)
validation_predict = base_clf.predict(validation_data_feat)


# ## classifier performance

# In[43]:


## accuracy helper
def get_accuracy(true_labels, predicted_labels):
    accuracies = {}
    
    predicted_classes = list(mlb.classes_)
    for cause_area in web_cause_area_select['cause area']:
        index = predicted_classes.index(cause_area)
        accuracy = accuracy_score(
            [a[index] for a in true_labels],
            [a[index] for a in predicted_labels]
        )
        accuracies[cause_area] = accuracy
        
    return accuracies


# on train data

# In[44]:


pre_optimization_train_acc = get_accuracy(train_data_label, train_predict)
pre_optimization_train_acc


# on test data

# In[45]:


get_accuracy(test_data_label, test_predict)


# on validation data (but **not** used as metric, since it will be used for next section)

# In[46]:


pre_optimization_validation_acc = get_accuracy(validation_data_label, validation_predict)
pre_optimization_validation_acc


# Q: mean train/test/validation accuracies

# In[47]:


print('mean train acc: %f' % np.average(list(pre_optimization_train_acc.values())))
print('mean test acc: %f' % np.average(list(get_accuracy(test_data_label, test_predict).values())))
print('mean validation acc: %f' % np.average(list(pre_optimization_validation_acc.values())))


# ## classification (optimization)
# improve model performance on test/validation data
# - since model does very well on train data, we don't need a more complex model
# - however, since test accuracy is far lower than train accuracy, model is overfitting
# - thus, reduce overfitting by optimizing model hyperparameters
# - use grid search to find best model hyperparameters

# #### complexity of current model
# random forest classifier parameters

# In[48]:


base_clf


# 1st decision tree's parameters

# In[49]:


base_clf.estimators_[0]


# max_depth and node_count of all decision trees

# In[50]:


def get_random_tree_statistics(random_tree):
    def get_attributes(tree):
        return {
            'max_depth': tree.max_depth,
            'node_count': tree.node_count,
        }
    
    return [get_attributes(t.tree_) for t in random_tree.estimators_]

base_clf_statistics = get_random_tree_statistics(base_clf)
base_clf_statistics


# Q: median tree max depth

# In[51]:


np.median([x['max_depth'] for x in base_clf_statistics])


# Q: median tree node count

# In[52]:


np.median([x['node_count'] for x in base_clf_statistics])


# #### bounds and parameters for grid search
# since the objective is to reduce model complexity, the following parameters can be explored to find the best hyperparameters for the model
# - n_estimators (5-50, increments of 5): lower = less overfitting
# - max_depth (5-20): lower = less overfitting
# - min_samples_leaf (1-10): higher = less overfitting
# - min_samples_split (2-10): higher = less overfitting

# In[53]:


n_estimators_range = range(5,50+1,10)
max_depth_range = range(5,20+1)
min_samples_leaf_range = range(1,10+1)
min_samples_split_range = range(2,10+1)


# generate hyperparameters

# In[54]:


from collections import namedtuple
import random

dt_hyperparameters = namedtuple('hyperparameters','n_estimators max_depth min_samples_leaf min_samples_split')
def create_dt_hyperparameters():
    return dt_hyperparameters(
        random.choice(n_estimators_range),
        random.choice(max_depth_range),
        random.choice(min_samples_leaf_range),
        random.choice(min_samples_split_range),
    )

dt_hyperparameters_list = [create_dt_hyperparameters() for x in range(1,100)]
dt_hyperparameters_list[:5]


# define classify function for hyperameter search

# In[55]:


def do_classify(model_params):
    clf = ensemble.RandomForestClassifier(
        n_estimators = model_params.n_estimators,
        max_depth = model_params.max_depth,
        min_samples_leaf = model_params.min_samples_leaf,
        min_samples_split = model_params.min_samples_split,
        n_jobs = -1)
    clf = clf.fit(train_data_feat, train_data_label)
    
    test_predict = clf.predict(test_data_feat)
    train_predict = clf.predict(train_data_feat)
    validation_predict = clf.predict(validation_data_feat)
    
    train_acc = get_accuracy(train_data_label, train_predict)
    test_acc = get_accuracy(test_data_label, test_predict)
    validation_acc = get_accuracy(validation_data_label, validation_predict)
    
    return {
        'model_params': model_params,
        'train_acc': train_acc,
        'test_acc': test_acc,
        'validation_acc': validation_acc,
        'mean_train_acc': np.average(list(train_acc.values())),
        'mean_test_acc': np.average(list(test_acc.values())),
        'mean_validation_acc': np.average(list(validation_acc.values())),
        'clf': clf,
    }


# do hyperparameter search

# In[56]:


experiment_results = [do_classify(params) for params in dt_hyperparameters_list]


# get hyperparameters with best mean test performance
# - ie. using test set to optimize hyperparameters

# In[57]:


top_hyperparameter = sorted(experiment_results, reverse=False, key=lambda e: e['mean_test_acc'])[0]
print("top hyperparameters: ", top_hyperparameter['model_params'])
print("mean train accuracy: %f" % top_hyperparameter['mean_train_acc'])
print("mean test accuracy: %f" % top_hyperparameter['mean_test_acc'])


# mean validation accuracy of model (ie. actual performance of model on unseen data)

# In[58]:


print("mean validation accuracy: %f" % top_hyperparameter['mean_validation_acc'])


# ## predict descriptions with fully trained model

# train random forest classifier with top hyperparameters and with all data

# In[59]:


def train_best_clf(model_params):
    best_clf = ensemble.RandomForestClassifier(
        n_estimators = model_params.n_estimators,
        max_depth = model_params.max_depth,
        min_samples_leaf = model_params.min_samples_leaf,
        min_samples_split = model_params.min_samples_split,
        n_jobs = -1)

    best_clf.fit(train_data_feat, train_data_label)
    best_clf.fit(test_data_feat, test_data_label)
    best_clf.fit(validation_data_feat, validation_data_label)
    
    return best_clf

best_clf = train_best_clf(top_hyperparameter['model_params'])


# predict descriptions of all entries (including organizations used for train/test/validation)

# In[60]:


def do_predict_cause_area_on_descriptions(df):
    descriptions = count_vectorizer.transform(df['desc_clean'])
    predictions_raw = best_clf.predict(descriptions)
    predictions = mlb.inverse_transform(predictions_raw)
    return [set(s) for s in predictions]

web_df['cause_area_predict'] = do_predict_cause_area_on_descriptions(web_df)
web_df['cause_area_predict_count'] = web_df['cause_area_predict'].apply(lambda c: len(c))


# Q: distribution of predicted cause areas for all organizations (nonempty descriptions)

# In[61]:


web_df.iloc[orgs_with_description_index]         ['cause_area_predict_count'].value_counts()


# Q: distribution of predicted cause areas for all unobserved organizations (nonempty descriptions)

# In[62]:


unobserved_observations_indexes = [n for n in orgs_with_description_index if n not in web_df_select.index]
web_df.iloc[unobserved_observations_indexes]     ['cause_area_predict_count'].value_counts()


# Note: **from these count distributions, we can see that the classifier isn't very good at imputing cause areas for new observations**

# define new row that uses predicted cause areas, and overwrites predicted cause areas if the 'ground truth' cause area is present

# In[63]:


web_df['cause_area_predict_final'] = web_df['cause_area_predict']

orgs_with_filtered_cause_areas =     web_df['cause_area_clean_filter'].apply(lambda s: s if len(s) > 0 else None).dropna().index
web_df['cause_area_predict_final'].loc[orgs_with_filtered_cause_areas] =     web_df['cause_area_clean_filter'].loc[orgs_with_filtered_cause_areas]
    
web_df.head()


# ## exporting results

# create new dataframe in kelvin's format (for use with tableau map viz)

# In[64]:


def to_kelvin_export_format(r):
    causes = list(r['cause_area_predict_final'])
    to_export = []
    
    for cause in causes:
        to_export.append(
            {
                'key': r['key'],
                'name': r['name'],
                'cause': cause,
            }
        )
        
    return to_export

to_export = list(chain.from_iterable([to_kelvin_export_format(row) for index, row in web_df.iterrows()]))


# In[65]:


to_export_df = pd.DataFrame(to_export)
to_export_df[:20]


# export dataframe to file

# In[66]:


to_export_df.to_csv(OUTPUT_PATH+'/classify_cause_area/kelvin_tableau_export.csv')

