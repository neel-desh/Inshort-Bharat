# import pyrebase
# #Firebase Config
# firebaseConfig = {
#     "apiKey": "AIzaSyDmRPCLhyOVASlBhHWwZ3slD0nZr9VWOlE",
#     "authDomain": "inshortbharat.firebaseapp.com",
#     "databaseURL": "https://inshortbharat-default-rtdb.firebaseio.com",
#     "projectId": "inshortbharat",
#     "storageBucket": "inshortbharat.appspot.com",
#     "messagingSenderId": "381240062652",
#     "appId": "1:381240062652:web:a99ed5dda628ddb59dd6b9",
#     "measurementId": "G-4ZP05FMFRR"
#   };
# firebase = pyrebase.initialize_app(firebaseConfig)
# storage = firebase.storage()

# #userid/postid/image_name
# storagePath = "1/1/bubuchan.png"
# localPath = "NeelBurgerFlyer.png"

# file = storage.child(storagePath).put(localPath)
# url = storage.child(storagePath).get_url(file['downloadTokens'])
# print(url)
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 

# def sentiment_scores(sentence):
#     sent_tag = ""
#     sid_obj = SentimentIntensityAnalyzer()
#     sentiment_dict = sid_obj.polarity_scores(sentence)
#     if(sentiment_dict['compound'] >= 0.05):
#         sent_tag = "Positive"
#     elif(sentiment_dict['compound'] <= -0.05): 
#         sent_tag = "Negative"
#     else:
#         sent_tag = "Neutral" 
#     return sent_tag

# print(sentiment_scores("HI how are you!"))
# from googletrans import Translator

# translator = Translator()
# result = translator.translate('Mikä on nimesi', src='fi', dest='fr')

# print(result.src)
# print(result.dest)
# print(result.text)
# from gensim.summarization.summarizer import summarize
# doc ="""Machine learning (ML) is the scientific study of algorithms and statistical models that computer systems use to progressively improve their performance on a specific task. Machine learning algorithms build a mathematical model of sample data, known as "training data", in order to make predictions or decisions without being explicitly programmed to perform the task. Machine learning algorithms are used in the applications of email filtering, detection of network intruders, and computer vision, where it is infeasible to develop an algorithm of specific instructions for performing the task. Machine learning is closely related to computational statistics, which focuses on making predictions using computers. The study of mathematical optimization delivers methods, theory and application domains to the field of machine learning. Data mining is a field of study within machine learning, and focuses on exploratory data analysis through unsupervised learning.In its application across business problems, machine learning is also referred to as predictive analytics."""
# print(summarize(doc))
from flask import Markup
import bs4
tag = Markup('<h1>Bishh</h1>')

soup = bs4.BeautifulSoup(tag,'html.parser')

print(soup.text)