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
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 

def sentiment_scores(sentence):
    sent_tag = ""
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    if(sentiment_dict['compound'] >= 0.05):
        sent_tag = "Positive"
    elif(sentiment_dict['compound'] <= -0.05): 
        sent_tag = "Negative"
    else:
        sent_tag = "Neutral" 
    return sent_tag

print(sentiment_scores("HI how are you!"))