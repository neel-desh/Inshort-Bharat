
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 

def sentiment_scores(sentence):
    sent_tag = ""
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    if(sentiment_dict['compound'] >= 0.05):
        sent_tag = "Positive"
    elif(sentiment_dict['compound'] <= - 0.05): 
        sent_tag = "Negative"
    else:
        sent_tag = "Neutral" 
    return sent_tag
print(sentiment_scores("Neel is bad person"))