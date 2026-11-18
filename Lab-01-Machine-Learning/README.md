# Lab 01: Machine Learning

## Objective

Practice basic natural language processing (NLP) tasks by preprocessing labelled review sentences, exploring sentiment language, and training a traditional machine learning classifier.

## Practical Information

- **Topic:** Text Preprocessing, TF-IDF and Machine Learning
- **Duration:** 1 hour
- **Programming language:** Python
- **Libraries:** Pandas, NumPy, NLTK, Scikit-learn, Matplotlib, Seaborn
- **Dataset:** [Sentiment Labelled Sentences](https://archive.ics.uci.edu/dataset/331/sentiment%2Blabelled%2Bsentences)

## Dataset

The notebook downloads the UCI dataset ZIP when it is not available locally, then loads the IMDb, Amazon, and Yelp sentence files. The loaded dataset has 3,000 sentences: 500 positive and 500 negative examples from each source. The dataset is licensed under CC BY 4.0; see the [UCI dataset page](https://archive.ics.uci.edu/dataset/331/sentiment%2Blabelled%2Bsentences) for attribution details.

## Tasks

1. Download and load the dataset.
2. Preprocess the text: lowercase it, remove punctuation and unnecessary characters, normalize whitespace, create a clean-text column, and compare original and cleaned text.
3. Explore positive and negative examples, frequent words, and differences between sentiment classes.
4. Split the dataset into training and test sets.
5. Create a bag-of-words (BOW) representation.
6. Train a machine learning model.
7. Evaluate accuracy, precision, recall, and F1 score.
8. Test the model with a new sentence.

## Implementation

The full practical, including code and executed outputs, is in the [Lab 01 notebook](notebook/lab_01_machine_learning.ipynb). Text is lowercased, punctuation and other non-alphanumeric characters are replaced with spaces, and repeated whitespace is collapsed. The dataset is split with stratification (80% training, 20% test; random state 42). A Logistic Regression classifier is trained on BOW features. A TF-IDF Logistic Regression model is also trained for comparison. Vectorizers are fitted on training text only.

## Results and Evidence

The test set contains 600 sentences (300 negative and 300 positive). The table reports positive-class precision, recall, and F1 alongside accuracy.

| Representation and model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| BOW + Logistic Regression | 0.822 | 0.816 | 0.830 | 0.823 |
| TF-IDF + Logistic Regression | 0.822 | 0.806 | 0.847 | 0.826 |

The BOW confusion matrix was 244 true negatives, 56 false positives, 51 false negatives, and 249 true positives. The example sentence “This product exceeded my expectations and I would gladly recommend it.” was predicted as **positive**, with estimated probabilities of 0.28 negative and 0.72 positive.

- [Word frequency comparison](screenshots/lab01_word_frequencies.svg)
- [Model evaluation chart and BOW confusion matrix](screenshots/lab01_model_evaluation.svg)

## Observations

The most frequent positive-class terms included “great” and “good”; frequent negative-class terms included “not,” “bad,” and “food.” Some words appeared in both classes because reviews cover different products, movies, and restaurants. On this split, BOW and TF-IDF had equal accuracy, while TF-IDF had slightly higher recall and F1. These results describe one held-out split and may change with a different split or dataset.

## Learning Outcomes

This practical demonstrates how text cleaning and vectorization turn sentences into features a classifier can use. It also shows why evaluation should include precision, recall, and F1 in addition to accuracy, and how BOW and TF-IDF can produce different trade-offs. The model relies on word patterns and may not handle sarcasm, context, or a change in review domain reliably.

