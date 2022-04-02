# -*- coding: utf-8 -*-
"""BERT_email_classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MbG7Ju626Mud7gexMttAO4ecJWbSSVkX

# Predict whether an Email is a spam or not
"""

!pip install tensorflow-text

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text

import pandas as pd

df = pd.read_csv("spam.csv")
df.head(5)

df.groupby('Category').describe()

"""## How to handle data imbalance
1. Use technique call down sampling
"""

df['Category'].value_counts()

747/4825

"""## What is Down Sampling technique to handle data imbalance
* ham email count 4825
* spam email count 747
* 15% is spam email and 85% is ham email making it imbalance so down sampling technique is to pick random ham 4825 and only get 747 samples to match  spam
* that way you will have equal number of ham and spam of 747

"""

# Create new dataframe spam
df_spam = df[df['Category']=='spam']
df_spam.shape

# Create new datafram ham
df_ham = df[df['Category']=='ham']
df_ham.shape

df_ham.sample(747)

# Create down sample of haw to 747
df_ham_downsampled = df_ham.sample(df_spam.shape[0])
df_ham_downsampled.shape

# concentename df_spam and df_ham_downsampled to make df_balanced
df_balanced = pd.concat([df_spam, df_ham_downsampled])
df_balanced.shape

df_balanced['Category'].value_counts()

df_balanced.sample(5)

# Create a new column turn ham and spam into 0 and 1
df_balanced['spam'] = df_balanced['Category'].apply(lambda x: 1 if x=='spam' else 0)
df_balanced.sample(10)

from sklearn.model_selection import train_test_split
X = df_balanced['Message']
y = df_balanced['spam']

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y)

X_train.head(4)

"""## Load trained model from tfhub.dev"""

# Use existing pre process

bert_preprocess = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")

# Use existing encoder
bert_encode = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4")

# function
# get_sentence_embeding(["500$ discount. hurry up", "bhavin, are up for up volley ball game?"]) ---> 768 len vector

def get_sentence_embeding(sentences):  
  preprocessed_text = bert_preprocess(sentences)
  return bert_encode(preprocessed_text)

get_sentence_embeding([
  "500$ discount. hurry up", 
  "bhavin, are up for up volley ball game?"
])

# test to see what this really means.  What is the benefit of this BERT encoding
e = get_sentence_embeding([
    "banana", 
    "grapes",
    "mango",
    "jeff bezos",
    "elon musk",
    "bill gates"
]
)

e

# Cosine of Similarity = 1 https://www.youtube.com/watch?v=m_CooIRM3UI
from sklearn.metrics.pairwise import cosine_similarity
cosine_similarity([e[0]],[e[1]])

"""Jeff bezos and Elon musk are more similar then Jeff bezos and banana as indicated above

**Build Model**
There are two types of models you can build in tensorflow.

(1) Sequential (2) Functional

So far we have built sequential model. But below we will build functional model. More information on these two is here: https://becominghuman.ai/sequential-vs-functional-model-in-keras-20684f766057
"""

# Bert Layers

text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name="text")
preprocessed_text = bert_preprocess(text_input)
outputs = bert_encode(preprocessed_text)

# Neural network Layers
l = tf.keras.layers.Dropout(0.1, name='dropout')(outputs['pooled_output'])
# second layer
l = tf.keras.layers.Dense(1, activation='sigmoid', name='output')(l)

# Construct final model
model = tf.keras.Model(inputs=[text_input], outputs=[l])

model.summary()

# Apply Metrics and compie model to get an idea how your model training is working
METRICS = [
  tf.keras.metrics.BinaryAccuracy(name='accuracy'),
  tf.keras.metrics.Precision(name='precision'),
  tf.keras.metrics.Recall(name='recall')
]

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=METRICS)

model.fit(X_train, y_train, epochs=10)

# Evaluate the model
model.evaluate(X_test, y_test)

y_predicted = model.predict(X_test)
y_predicted = y_predicted.flatten()

# if the value > 0.5 set 1 else set to 0
import numpy as np

y_predicted = np.where(y_predicted > 0.5, 1, 0)
y_predicted

# Plot a confusion metrics
from sklearn.metrics import confusion_matrix, classification_report

cm = confusion_matrix(y_test, y_predicted)
cm

# plot the confusion metrics
from matplotlib import pyplot as plt 
import seaborn as sn 
sn.heatmap(cm, annot=True, fmt='d')
plt.xlabel('Predicted')
plt.ylabel('Truth')

"""### not spam = 177 correct, predict wrong 10 times
 predict spam = 166 correct, predict wrong 21 times

* True Positive = 177
* False Positive = 10
* False Negative = 21
* True Negative = 166



"""

print(classification_report(y_test, y_predicted))

reviews = [
    'Reply to win Â£100 weekly! Where will the 2006 FIFA World Cup be held? Send STOP to 87239 to end service',
    'You are awarded a SiPix Digital Camera! call 09061221061 from landline. Delivery within 28days. T Cs Box177. M221BP. 2yr warranty. 150ppm. 16 . p pÂ£3.99',
    'it to 80488. Your 500 free text messages are valid until 31 December 2005.',
    'Hey Sam, Are you coming for a cricket game tomorrow',
    "Why don't you wait 'til at least wednesday to see if you get your ."
]
model.predict(reviews)

# Save the entire model as a SavedModel.
!mkdir -p saved_model
model.save('saved_model/my_model')

# my_model directory
!ls saved_model

# Contains an assets folder, saved_model.pb, and variables folder.
!ls saved_model/my_model

# load my model
new_model = tf.keras.models.load_model('saved_model/my_model')

# Check its architecture
new_model.summary()

# use new_model to predicted review
new_model.predict(reviews)

# zip model
!zip -r spammodel.zip saved_model/my_model

# use this library to download zip file saved model
from google.colab import files

files.download('spammodel.zip')

