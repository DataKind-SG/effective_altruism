---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.0'
      jupytext_version: 0.8.4
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  language_info:
    codemirror_mode:
      name: ipython
      version: 3
    file_extension: .py
    mimetype: text/x-python
    name: python
    nbconvert_exporter: python
    pygments_lexer: ipython3
    version: 3.6.1
---

# EA x DKSG
**classification: ea**

classify cause area keywords -> cause areas
- expert knowledge & elbow grease from EA team

## (tldr);
- decided against the approach of the generating random features and modelling the features as a multiclass problem
    - random features are likely not to have the same distribution of words as observed in web scraped descriptions
    - search space is too large (too many permutations of possible features)
    - multilabel occurences are rare; most organizations only have 1-3 cause areas
    - since multilabel occurences are rare, multilabel approach may not work so well given that multilabel observations are sparse

## methodology
- clean up cause keywords
    - drop stopwords
    - drop punctuations
- create count vectors for each cause area keyword set
- use count vectors as feature for classification with
    - decision tree
    
## hypothesis
given a cause area's list of keywords, i should be able to distinguish each cause area uniquely.

## goal
1. create a model that can distinguish each cause area based on cause area keywords
2. capture related concepts based on existing keywords in each cause area
3. do 1 and 2 with as simple a model as possible (for interpretability)


## setup

```python
## setup
%run setup/env_setup.py
%run ../common/filepaths.py
%run ../common/helpers.py
```

## clean up cause area keywords

```python
## ml setup
import sklearn
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelBinarizer
from sklearn import tree
from sklearn import ensemble
from sklearn.metrics import accuracy_score
```

```python
ea_df = read_from_csv(EA_CSV)
```

```python
ea_df['keywords_clean_words'] = get_cleaned_descriptions(list(ea_df[KEYWORDS_COLUMN]), True, True, False, True)
ea_df['keywords_clean'] = get_sentence_from_list(list(ea_df['keywords_clean_words']))
```

```python
ea_df.head()
```

Q: all cause areas

```python
ea_df['Causes/ Columns']
```

## create features
#### create cross-cause area keyword groupings
create sentences of words which correspond to their cause areas

given a set of keywords: 

1) "HIV, AIDs, Clinic" -> Diseases

2) "Recycle, water, plastic" -> Environment

generate the following features for each cause area:

1) **standalone features**:
eg. ([hiv], [diseases]), ([aids], [diseases]) ...

2) **intra-group features**: 
eg. ([hiv,aids], [diseases]), ([aids,clinic], [diseases])

3) **inter-group features**: 
eg. ([hiv,recycle],[diseases,environment]), ([aids,clinic,water,plastic],[diseases,environment]) 

by generating such features, we can train the model to perform multiclass-multilabel classification


#### standalone features 

```python
from collections import namedtuple

words_causes = namedtuple('words_causes','words causes')
features = []
```

(note: work not continued, code is just spike approach to generate extended sample)

```python
from itertools import chain, combinations

def generate_standalone_features(df):
    features = {}
    for _, row in df.iterrows():
        cause_area = row['Causes/ Columns']
        keywords = row['Keywords_Set 1'].strip()
        
        feature_units = [w.strip() for w in keywords.split(",")]
        feature_units = [w for w in feature_units if len(w) > 0]
        feature_units = [words_causes([w], set([cause_area])) for w in feature_units]
        features[cause_area] = feature_units
        
    return features

standalone_features_map = generate_standalone_features(ea_df)
standalone_features = list(chain(*standalone_features_map.values()))

def generate_extended_features(standalone_features, max_n_choose):
    extended_features = []
    
    standalone_features_list = list(chain(standalone_features))
    standalone_features_count = len(standalone_features_list)
    
    for n_choose in range(2, max_n_choose+1):
        extended_features = extended_features + list(combinations(standalone_features_list,n_choose))
        
    def transform_feature_group(features):
        keywords = list(list(chain.from_iterable([w.words for w in features])))
        cause_areas = set(chain.from_iterable([w.causes for w in features]))
        return words_causes(keywords, cause_areas)
        
    extended_features = [transform_feature_group(f) for f in extended_features]
    return extended_features

n_cause_areas = len(ea_df['Causes/ Columns'])
n_cause_areas = 2
extended_features = generate_extended_features(standalone_features,n_cause_areas)
```

```python
print("number of extended features: %d" % len(extended_features))
```

```python
extended_features[1:10]
```

```python
extended_features[100:110]
```

#### count vectors for each cause area

```python
count_vectorizer = CountVectorizer(binary=False)

data_feat = count_vectorizer.fit_transform(ea_df['keywords_clean'])
```

## create labels: cause areas

```python
lb = LabelBinarizer()
data_label = list(ea_df['Causes/ Columns']) 
data_label_transform = lb.fit_transform(data_label)
```

## classify and predict (basic)
- since classifier's performance varies by random state, iterate multiple times to see average model performance

```python
def do_classify_dt(random_state=None):
    base_clf = tree.DecisionTreeClassifier(random_state=random_state)
    base_clf.fit(data_feat, data_label_transform)
    
    train_predict_feat = base_clf.predict(data_feat)
    train_predict = lb.inverse_transform(train_predict_feat)
    
    acc = accuracy_score(data_label, train_predict)
    
    return (base_clf, acc)
```

```python
base_clf_random_state = range(50)
base_clf_experiments = [do_classify_dt(i) for i in base_clf_random_state]

base_clf_avg_acc = np.average([acc for (clf,acc) in base_clf_experiments])
print('base classifier mean accuracy: %f' % base_clf_avg_acc)
```
