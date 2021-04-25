from time import time
from flask import *
import hashlib
import os
import flask
from werkzeug.utils import secure_filename
import requests
import mysql.connector
import random
from flask_mail import Mail, Message
from newsapi import NewsApiClient
from flask_simple_geoip import SimpleGeoIP
import openweather
import datetime
import re
import pyrebase
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
from googletrans import Translator
from flask import Markup
from gensim.summarization.summarizer import summarize
import bs4
import pickle
# import COVID19Py
import emailsender as ty
from covid import Covid


latest_covid = {}
covid = Covid(source="worldometers")
covid.get_data()

latest_covid["active"] = covid.get_total_active_cases()
latest_covid["confirmed"] = covid.get_total_confirmed_cases()
latest_covid["recovered"] = covid.get_total_recovered()
latest_covid["deaths"] = covid.get_total_deaths()

# try:
#     covid19 = COVID19Py.COVID19()
#     covid19 = COVID19Py.COVID19(data_source="jhu")
#     latest_covid = covid19.getLatest()
# except Exception as e:
#     covid19 = COVID19Py.COVID19()
#     covid19 = COVID19Py.COVID19(data_source="csbs")
#     latest_covid = covid19.getLatest()



pickle_in = open(r'./model.pickle','rb')
classifier = pickle.load(pickle_in)

#Firebase Config
firebaseConfig = {
    "apiKey": "AIzaSyDmRPCLhyOVASlBhHWwZ3slD0nZr9VWOlE",
    "authDomain": "inshortbharat.firebaseapp.com",
    "databaseURL": "https://inshortbharat-default-rtdb.firebaseio.com",
    "projectId": "inshortbharat",
    "storageBucket": "inshortbharat.appspot.com",
    "messagingSenderId": "381240062652",
    "appId": "1:381240062652:web:a99ed5dda628ddb59dd6b9",
    "measurementId": "G-4ZP05FMFRR"
  };
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()


# create client
ow = openweather.OpenWeather()

app = Flask(__name__,template_folder='templates')
app.secret_key = 'this is a very secure string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(GEOIPIFY_API_KEY='at_v1LEHVAlNSSUFAb6T3ONOJcNdy2WU')
newsapi = NewsApiClient(api_key="18cd6534eefc44db90cb02e7ef2cb9fc")
simple_geoip = SimpleGeoIP(app)
translator = Translator()

# Email config
app.config['MAIL_SERVER']='smtp.stackmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'sem6@neeldeshmukh.com'
app.config['MAIL_PASSWORD'] = 'Gr5d4aa42'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
# Mysql connection
try:
    database = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="inshort_bharat"
    )
    # database = mysql.connector.connect(
    # host="mysql.stackcp.com",
    # user="inshortbharat-313731ad7f",
    # password="36811b7ybn",
    # database="inshortbharat-313731ad7f",
    # port=53505
    # )
    print("Connection Success")
except Exception as e:
    print(e)

# Common Functions
def slug_gen(title):
    """Remove Bad charater and add - where space & trims it"""
    
    trim_url = title.rsplit('/', 1)[-1]
    cleanString = re.sub('\W+','-', trim_url )
    return cleanString.lower()

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

##==========
##* Index
##==========
@app.route('/')
def index():
    categories = [
                { "name" : "accounting", "image" : "https://images.pexels.com/photos/53621/calculator-calculation-insurance-finance-53621.jpeg" },
                { "name" : "technology", "image" : "https://images.pexels.com/photos/4842496/pexels-photo-4842496.jpeg" },
                { "name" : "astrology", "image" : "https://images.pexels.com/photos/1275413/pexels-photo-1275413.jpeg" },
                { "name" : "crime", "image" : "https://images.pexels.com/photos/923681/pexels-photo-923681.jpeg" },
                { "name" : "education", "image" : "https://images.pexels.com/photos/3059750/pexels-photo-3059750.jpeg" },
                { "name" : "cricket", "image" : "https://images.pexels.com/photos/3718433/pexels-photo-3718433.jpeg" }
                ]
    geoip_data = simple_geoip.get_geoip_data()
    location = geoip_data['location']
    city = location['city']
    weather_data = get_weather("mumbai")
    print(weather_data)
    headline = ""
    all_headlines = newsapi.get_top_headlines(category="general",
    language='en',country="in")
    news_articles = all_headlines.get('articles')
    print("news headlines", news_articles)
    for news in news_articles:
        headline += news['title'] + " "
    news_list = []
    query = 'SELECT id, title, content, published_date, image, category, slug FROM news ORDER BY published_date ASC LIMIT 10'
    with database.cursor() as cursor:
        cursor.execute(query)
        db_data = cursor.fetchall()
        for row in db_data:
            news = {}
            #print(row[1],row[2])
            news['id'] = row[0]
            news['title'] = row[1]
            news['content'] = row[2]
            news['date'] = row[3]
            news['image'] = row[4]
            news['category'] = row[5]
            news['slug'] = row[6]
            news_list.append(news)
    return render_template("index.html",
                            headlines=headline,
                            location=location,
                            weather_data=weather_data,
                            day=datetime.datetime.today().strftime('%d'),month=datetime.datetime.today().strftime('%h'),
                            newslist=news_list,
                            categorylist=categories,
                            covid = latest_covid)

#date article reference : https://stackoverflow.com/questions/28189442/datetime-current-year-and-month-in-python
##==========
##* Change Language
##==========
@app.route('/changelang',methods=['GET','POST'])
def changelang():
    lang = request.form['lang']
    if lang:
        session['language'] = lang
        return "Success"

#
#* Scraper & application object store
#
# @app.context_processor
# def category_data():
#     response_obj = newsapi.get_everything(
#                                     language='en',
#                                     q='Technology')
#     Tech_all_articles = response_obj["articles"]
#     response_obj1 = newsapi.get_everything(
#                                     language='en',
#                                     q='entertainment')
#     Entertainment_all_articles = response_obj1["articles"]
#     articles = {}
#     articles["technology"] = Tech_all_articles
#     articles["entertainment"] =Entertainment_all_articles
#     return dict(articles = articles)

#
# Blog.html is used here. make other blog page for non scrape articles later
#    
#Tech route
# @app.route('/technology')
# def techo_articles():
#     return render_template("news/blog.html",category='technology')

# #entertainment route
# @app.route('/entertainment')
# def entertain_articles():
#     return render_template("news/blog.html",category='entertainment')

# @app.route('/article/<category>/<title>',methods=['GET','POST'])
# def scrape_article(category,title):
#     category = category
#     title = title
#     return render_template("news/blog-details-scraped.html",category = category, title = title)
#
# get weather data
#
def get_weather(city):
    api_key = "c52849616ef144426eacbab437ebe3a8"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = city
    weather_data = {
    }
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name 
    response = requests.get(complete_url) 
    x = response.json() 
    if x["cod"] != "404": 
        y = x["main"] 
        weather_data["celcius"] = round(int(y["temp"]) - 273.15,2)
        weather_data["humidity"] = y["humidity"] 
        z = x["weather"] 
        weather_data["desc"] = z[0]["description"]  
    return weather_data




@app.route('/category/<category_name>',methods=['GET','POST'])
def category_scrape(category_name):
    #TODO: RETURN CATEGORY
    category_namee = category_name
    news_list = []
    query = """SELECT news.id, title, content, MONTHNAME(published_date), image, category, slug, users.name, count(comments.comment), DATE_FORMAT(published_date,"%D")
               FROM news             
               LEFT JOIN users ON news.published_by = users.id
               LEFT JOIN comments ON news.id = comments.post_id
               WHERE category = %s """
    print(query)
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query,(category_namee,))
        db_data = cursor.fetchall()
        news = {}
        for row in db_data:
            print(row)
            news['id'] = row[0]
            news['title'] = row[1]
            news['content'] = row[2]
            news['month'] = row[3]
            news['image'] = row[4]
            news['category'] = row[5]
            news['slug'] = row[6]
            news['name'] = row[7]
            news['commentcount'] = row[8]
            news['day'] = row[9]

            news_list.append(news)
    return render_template("news/blog-grid.html", categories = news_list)
        


##==========
##* Web Stories
##==========
@app.route('/web-stories')
def webstories():
    stories = []
    i = 1
    all_headlines = newsapi.get_top_headlines(category="general",
    language='en',country="in")
    news_articles = all_headlines.get('articles')
    for news in news_articles:
        data = {}
        data["id"] = i
        data["head"] = news['title']
        data["src"] = news['urlToImage']
        data["content"] = news['description']
        stories.append(data)
        i += 1
    return render_template("news/stories.html",stories=stories)

##?================================================
##TODO: News Display Pages
##? 

##==========
##TODO: news
##==========
@app.route('/news',methods=['GET','POST'])
def news():
    #TODO: LIST NEWS recent
    news_list = []
    query = 'SELECT id, title, content, published_date, published_by, category, slug FROM news ORDER BY published_date ASC LIMIT 50'
    with database.cursor() as cursor:
        cursor.execute(query)
        db_data = cursor.fetchall()
        for row in db_data:
            news = {}
            #print(row[1],row[2])
            news['id'] = row[0]
            news['title'] = row[1]
            news['content'] = row[2]
            news['date'] = row[3]
            news['author'] = row[4]
            news['category'] = row[5]
            news['slug'] = row[6]
            news_list.append(news)
    print(news_list)
    return render_template("news/blog.html",news_list=news_list)

##==========
##TODO: news-grids
##==========
# @app.route('/news-grids')
# def newsgrids():
#     return render_template("news/blog-grid.html")

##==========
##TODO: news detail page
##==========
@app.route('/dp/<category>/<slug>',methods=['GET','POST'])
def dp(category,slug):
     
    news = {}
    # Query fetches news and publisher details
    query = """
            SELECT
                news.id,
                title,
                content,
                published_date,
                image,
                tags,
                users.name,
                users.image_url,
                facebook,
                instagram,
                linkedin,
                twitter,
                google
            FROM
                news
            LEFT JOIN users ON news.published_by = users.id
            LEFT JOIN social ON users.id = social.user_id
            WHERE
                slug = %s AND category = %s
            """
    print(query)
    data = (slug, category)
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query,data)
        db_data = cursor.fetchall()
        for row in db_data:
            #print(row[1],row[2])
            news['id'] = row[0]
            news['title'] = row[1]
            news['content'] = Markup(row[2])
            news['date'] = row[3]
            news['headerimg'] = row[4]
            news['tags'] = row[5]
            news['authorname'] = row[6]
            news['authorimg'] = row[7]
            news['facebook'] = row[8]
            news['instagram'] = row[9]
            news['linkedin'] = row[10]
            news['twitter'] = row[11]
            news['google'] = row[12]    
    
    if session.get("language",0):
        if session['language'] == 'Hindi':        
            result = translator.translate(news['content'], src='en',dest='hi')
            news['content'] = result.text
            result = translator.translate(news['title'], src='en',dest='hi')
            news['title'] = result.text
    #Comment
    comment_list = []
    print(news)
    nquery = "SELECT comments.id, users.name, comment, sentiment, timestamp, users.image_url, comments.user_id FROM comments LEFT JOIN users ON comments.user_id = users.id WHERE post_id = "+ str(news['id'])+""
               
    with database.cursor(buffered=True) as cursor:
        cursor.execute(nquery)
        db_data = cursor.fetchall()
        for row in db_data:
            #print(row[1],row[2])
            print(row)
            comment = {}
            comment['id'] = row[0]
            comment['name'] = row[1]
            comment['comment'] = row[2]
            comment['sentiment'] = row[3]
            comment['timestamp'] = row[4]
            comment['user_img'] = row[5]
            comment['user_id'] = row[6]
            comment_list.append(comment)
    print(comment_list)
    return render_template("news/blog-details.html",news=news,comments=comment_list)

##?
##TODO: News Display Pages End
##?================================================


##?================================================
##TODO: Authentication Pages
##? Login, Register, VerifyOTP, ForgotPassword, ResetPassword, Logout

##==========
##TODO: Login
##==========
@app.route('/login',methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            password = hashlib.md5(password.encode()).hexdigest()
            print(email)
            query = 'Select id, name, email, password, type, image_url from users where email = %s and password = %s'
            data = (email,password)
            with database.cursor() as cursor:
                cursor.execute(query,data)
                db_data = cursor.fetchall()
                for row in db_data:
                    print("helpppppppppp")
                    print(db_data)
                    if row[2] == email and row[3] == password:
                        print(row)
                        session['user_id'] = row[0]
                        session['name'] = row[1]
                        session['email'] = email
                        session['account_type'] = row[4]
                        session['user_img'] = row[5]
                        return redirect(url_for('index'))
        except Exception as e:
            print(e)
            database.rollback()
            err = "some error occured! try again."     
    return render_template("authentication/login.html")

##==========
##TODO: Register
##==========
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
       # try:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        account_type = request.form['acc_type']
        OTP = random.randint(1000,9999)
        #send otp to user on email
        print(OTP)
        user_info = {
            "name" : name,
            "email" : email,
            "password": hashlib.md5(password.encode()).hexdigest(),
            "account_type" : account_type,
            "OTP" : OTP
        }
        session['user_info'] = user_info
        msg = Message('Here is OTP to verify!', sender = 'sem6@neeldeshmukh.com',
                                recipients = [email])
        msg.html = str(ty.giveHtml(str(OTP),name))
        mail.send(msg)           
        # except Exception as e:      
        #     print(e)      
        #     err = "some error occured! try again."
        return redirect(url_for('verifyotp'))
        
    return render_template("authentication/register.html")

##==========
##TODO: VerifyOTP
##==========
@app.route('/verify-otp',methods=['GET','POST'])
def verifyotp():
    if request.method == 'POST':
        # try:
        print("1")
        user_info = session.get('user_info')
        print("2")
        print(user_info)
        otp = request.form['OTP']
        print(otp == user_info['OTP'])
        print("3")
        if (int(otp) != int(user_info['OTP'])):
            return render_template_string("Error Aya!")
        else:
            print("In IF")
            #global database 
            query = "INSERT INTO users(name, email, password, type, image_url) VALUES (%s,%s,%s,%s,%s)"
            data = (user_info["name"], user_info["email"],user_info["password"],user_info["account_type"],"https://i.picsum.photos/id/1011/5472/3648.jpg?hmac=Koo9845x2akkVzVFX3xxAc9BCkeGYA9VRVfLE4f0Zzk")
            with database.cursor() as cursor:
                print("IN cursor")
                cursor.execute(query,data)
                database.commit()
            session.pop('user_info', None)
            return redirect(url_for('login'))
        # except Exception as e:
        #     print(e)
            #database.rollback()
    return render_template("authentication/verify.html")

##==========
##TODO: Forgot Password
##==========
@app.route('/forgot-password',methods=['GET','POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form["email"]
        OTP = random.randint(1000,9999)
        session["fp-otp"] = OTP
        session['fpemail'] = email
        msg = Message('OTP', sender = 'sem6@neeldeshmukh.com',
                        recipients = [email])
        msg.body = "ForgotPass OTP: " + str(OTP)
        mail.send(msg)
        return redirect(url_for('verifyotpfp'))
    return render_template("authentication/forgotpassword.html")

@app.route('/verify-otp-fp',methods=['GET','POST'])
def verifyotpfp():
    if request.method == 'POST':
        otp = request.form['OTP']
        OTP = session["fp-otp"]
        if int(otp) == int(OTP):
            session.pop("fp-otp",None)
            session["fp-otp-verified"] = True
            return redirect(url_for("changefp"))
    return render_template("authentication/forgot-verify.html")

@app.route('/change-fp',methods=['GET','POST'])
def changefp():
    if request.method == 'POST':
        if session["fp-otp-verified"]:
            new_pass = request.form['newpassword']
            new_pass = hashlib.md5(new_pass.encode()).hexdigest()
            update_query = "UPDATE users SET password = %s WHERE email = %s"
            update_data = (new_pass,str(session["fpemail"]))
            with database.cursor(buffered=True) as cursor:
                cursor.execute(update_query,update_data)
                database.commit()
            return redirect(url_for('login'))        
        else:
            return render_template_string("Error Bad Person U")
    return render_template("authentication/forgot-changepass.html")
##==========
##TODO: Logout
##==========
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

##?
##?TODO: Authentication Pages END
##?================================================

##?================================================
##?TODO: User Profile & Dashboard Pages
##? Account, Edit Account, View Bookmarked News, View Liked News, Account Preferences

##==========
##TODO: Account
##==========
@app.route('/account')
def account():
    #TODO: login Check
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    # List Favourites here
    user_id = session["user_id"]
    query = "SELECT favorites.id, title, slug, news.category, timestamp FROM favorites LEFT JOIN news on favorites.post_id = news.id WHERE favorites.user_id = "+str(user_id)+""

    with database.cursor(buffered=True) as cursor:
        cursor.execute(query)
        db_data = cursor.fetchall()
        favourites = []
        for row in db_data:
            fav = {}
            fav["id"] = row[0]
            fav["title"] = row[1]
            fav["slug"] = row[2]
            fav["category"] = row[3]
            fav["timestamp"] = row[4]
            favourites.append(fav)
        
    return render_template("profile/account.html",favs = favourites)
##==========
##TODO: Edit Account
##==========
@app.route('/edit-account')
def editaccount():
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    return render_template("profile/dashboard-edit-profile.html")

##==========
##TODO: View
##==========
@app.route('/view-bookmarked')
def viewbookmarked():
    #TODO: login Check
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    # List Read Later here
    user_id = session["user_id"]
    query = "SELECT readlater.id, title, slug, news.category, timestamp, news.image FROM readlater LEFT JOIN news on readlater.post_id = news.id WHERE readlater.user_id = "+str(user_id)+""
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query)
        db_data = cursor.fetchall()
        readlaters = []
        for row in db_data:
            fav = {}
            fav["id"] = row[0]
            fav["title"] = row[1]
            fav["slug"] = row[2]
            fav["category"] = row[3]
            fav["timestamp"] = row[4]
            fav["image"] = row[5]
            readlaters.append(fav)
    #make sure u copy the template or jinja2 part from favourites to here!
    return render_template("profile/dashboard-bookmark.html",readlaters = readlaters)

##==========
##TODO: Add to Favourite
##==========
@app.route('/at-fav/<id>',methods=['GET','POST'])
def at_fav(id):
    #TODO: Login Check Not Added Yet
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    news_id = id
    query = "INSERT INTO favorites(post_id, user_id) VALUES (%s,%s)"
    print(news_id,session['user_id'] )
    data = (news_id,session['user_id'])
    with database.cursor() as cursor:
        cursor.execute(query,data)
        database.commit()   
    return jsonify({'msg':'Added To Fav'})
##==========
##TODO: Remove to Favourite
##==========
@app.route('/rm-fav/<id>',methods=['GET','POST'])
def rm_fav(id):
    #TODO: Login Check Not Added Yet
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    news_id = id
    print(news_id, session["user_id"])
    query = "DELETE FROM favorites WHERE id = "+ str(news_id) +" AND user_id ="+ str(session["user_id"]) +""
    with database.cursor() as cursor:
        cursor.execute(query)
        database.commit()   
    return jsonify({'msg':'Remove To Fav'})

##==========
##TODO: Add to Read Later
##==========
@app.route('/at-rl/<id>',methods=['GET','POST'])
def at_rl(id):
    #TODO: Login Check Not added
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    news_id = id
    query = "INSERT INTO readlater(post_id, user_id) VALUES (%s,%s)"
    print(news_id,session['user_id'] )
    data = (news_id,session['user_id'])
    with database.cursor() as cursor:
        cursor.execute(query,data)
        database.commit()   
    return jsonify({'msg':'Added To Readlater'})

##==========
##TODO: Remove from Read Later
##==========
@app.route('/rm-rl/<id>',methods=['GET','POST'])
def rm_rl(id):
    #TODO: Login Check Not Added Yet
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    news_id = id
    print(news_id, session["user_id"])
    query = "DELETE FROM readlater WHERE id = "+ str(news_id) +" AND user_id ="+ str(session["user_id"]) +""
    with database.cursor() as cursor:
        cursor.execute(query)
        database.commit()   
    return jsonify({'msg':'Removed from Read Later'})



##?
##?TODO: User Profile & Dashboard Pages END
##?================================================

##TODO: Common Edit Profile Functions

##==========
##TODO: ChangePassword
##==========
@app.route('/change-password',methods=['POST', 'GET'])
def changepassword():
    #TODO: Login Check
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session["user_id"]
        #check if current password is correct
        password = request.form['password']
        password = hashlib.md5(password.encode()).hexdigest()

        new_pass = request.form['newpassword']
        new_pass = hashlib.md5(new_pass.encode()).hexdigest()

        query = 'SELECT id, password from users WHERE id='+str(user_id)+''
        data = (int(user_id))
        with database.cursor(buffered=True) as cursor:
            cursor.execute(query)
            db_data = cursor.fetchall()
            for row in db_data:
                if row[1] == password:
                    #update with the new password
                    update_query = "UPDATE users SET password = %s WHERE id = %s"
                    update_data = (new_pass,user_id,)
                    with database.cursor(buffered=True) as cursor:
                        cursor.execute(update_query,update_data)
                        database.commit()
                    #return logout and relogin after password change
                    return redirect(url_for('logout'))
    else:
        return "None"

##==========
##TODO: Basic Info
##==========
@app.route('/update-basicinfo',methods=['POST', 'GET'])
def basicInfo():
    #TODO: Login Check
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session["user_id"]
        
        full_name = request.form['fname']
        query = "UPDATE users SET name=%s WHERE id=%s"
        data = (full_name,int(user_id))
        with database.cursor(buffered=True) as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"
    else:
        return "None"

##==========
##TODO: Avatar User Image
##==========
@app.route('/addProfImg',methods=['POST', 'GET'])
def addProfileImage():
    #TODO: Login Check
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session["user_id"]
        #TODO: check if image exist
        image = request.files['image']
        image_link = ""
        #TODO: add Image to Firebase and add link in mysql
        query = "UPDATE users SET image_url=%s WHERE id = %s"
        if image:
            filename = secure_filename(image.filename)
            storagePath = "profile/" + str(session["user_id"]) + "/"+ filename
            image_link = uploadImageFirebase(image,storagePath)
            data = (image_link,int(user_id))
            with database.cursor(buffered=True) as cursor:
                cursor.execute(query,data)
                database.commit()
                return "Success"
    else:
        return "Not Updated"
##==========
##TODO: Social Accounts
##==========
@app.route('/social-links',methods=['POST', 'GET'])
def sociallinks():
    #TODO: Login Check
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session["user_id"]
        facebook = request.form["facebook"]
        instagram = request.form["instagram"]
        twitter = request.form["twitter"]
        linkedin = request.form["linkedin"]
        google = request.form["google"]
        query = "UPDATE social SET facebook=%s, instagram=%s, twitter=%s, linkedin=%s, google=%s WHERE user_id = %s"
        #Get more data from form here
        data = (facebook, instagram,twitter,linkedin,google,int(user_id))
        with database.cursor(buffered=True) as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"
    else:
        return "None"   

##==========
##TODO: Delete Account
##==========
@app.route('/delete-account',methods=['POST', 'GET'])
def delaccount():
    #TODO: Login Check
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session["user_id"]
        #check if current password is correct
        password = request.form['password']
        password = hashlib.md5(password.encode()).hexdigest()

        query = "SELECT id, password, email from users WHERE id = "+ str(user_id)+""
        
        with database.cursor(buffered=True) as cursor:
            cursor.execute(query)
            db_data = cursor.fetchall()
            for row in db_data:
                if row[1] == password and row[2] == session['email']:
                    update_query = "DELETE from users WHERE id = "+ str(user_id)+""
                    update_data = (user_id)
                    with database.cursor(buffered=True) as cursor:
                        cursor.execute(update_query)
                        database.commit()
                    #return logout and relogin after password change
                    return redirect(url_for('logout'))
    else:
        return redirect(url_for('index'))

##?================================================
##?TODO: Admin Profile & Dashboard Pages END
##? Account, Edit Account, Create News, Edit News, Account Preferences

##==========
##TODO: Admin Account
##==========
@app.route('/admin-account')
def adminaccount():
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    #TODO: List Published news
    #SORT with date
    query = "SELECT id, title, published_date FROM news WHERE published_by =" + str(session['user_id']) +""
    recent_published_news = []
    
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
        for row in data:
            news = {}
            news['id'] = row[0]
            news['title'] = row[1]
            news['published_date'] = row[2]
            print(row)
            recent_published_news.append(news)
            
    return render_template("profile/admin/admin-account.html",newslist=recent_published_news)

##==========
##TODO: Admin Edit Account
##==========
@app.route('/admin-edit-account')
def admineditaccount():
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    query = "SELECT * FROM social WHERE user_id = " + str(session["user_id"]) + ""
    with database.cursor() as cursor:
        cursor.execute(query)
        myresult = cursor.fetchall()
        social = {}
        for row in myresult:
            social['facebook'] = row[2]
            social['instagram'] = row[3]
            social['twitter'] = row[4]
            social['linkedin'] = row[5]
            social['google'] = row[6]
    return render_template("profile/admin/admin-dashboard-edit-profile.html",social=social)

##==========
##TODO: Create Admin - News
##==========
@app.route('/create-news',methods=['GET','POST'])
def admincreatenews():
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    if request.method == 'POST':
        title = request.form['news-title']
        slug = slug_gen(title)
        image_link = ""
        #upload this to firebase storage and get url
        header_image = request.files['image']
        if header_image:
            filename = secure_filename(header_image.filename)
            storagePath = "uploads/" + str(session["user_id"]) + "/"+ filename
            image_link = uploadImageFirebase(header_image,storagePath)
            #header_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        category = request.form['category']
        tags = request.form['tags']
        content = request.form['content-news']
        locality = request.form['locality']
        send_bulk = request.form['bulk-email']
        print(title,slug,category,content,locality,send_bulk,image_link)
        #TODO: News Insert
        query = "INSERT INTO news(title, content, image, slug, category, tags, published_by, location) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        data = (title,content,image_link,slug,category,tags,session['user_id'],locality)
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
        return "news created"
    
    return render_template("profile/admin/admin-dashboard-post-news.html")

##==========
##TODO: Manage Admin - News
##==========
@app.route('/edit-news',methods=['GET','POST'])
def admineditnews():
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    #TODO: Just list the news created by this user give options liked edit, delete and read
    query = "SELECT id, title, published_date, category, slug FROM news where published_by = "+ str(session["user_id"])+""
    createdby_news_list = []
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query)
        db_data = cursor.fetchall()
        print(db_data)
        for row in db_data:
            news = {}
            print(row)
            news["id"] = row[0]
            news["title"] = row[1]
            news["date"] = row[2]
            news["category"] = row[3]
            news["slug"] = row[4]

            createdby_news_list.append(news)
            
    return render_template("profile/admin/admin-dashboard-manage-news.html",newslist=createdby_news_list)

##==========
##TODO: Edit Admin DATA - News
##==========
@app.route('/editnews/<nid>',methods=['GET','POST'])
def admineditnewsdata(nid):
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    #TODO: fill the data with news 
    query = "SELECT title, content, image, category, tags FROM news where id =" + str(nid) + " AND published_by = " + str(session['user_id']) + ""
    news = {}
    news["id"] = nid
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query)
        db_data = cursor.fetchall()
        for row in db_data:
            news["title"] = row[0]
            news["content"] = row[1]
            news["image"] = row[2]
            news["category"] = row[3]
            news["tags"] = row[4]
    return render_template("profile/admin/admin-dashboard-edit-news.html",news=news)

@app.route('/editnewsdata',methods=['POST'])
def newsdata():
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))    
    if request.method == 'POST':
        try:
            id = request.form["id"]
            title = request.form['title']
            backupimage = request.form['backupimage']
            image_link = ""
            #upload this to firebase storage and get url
            header_image = request.files['image']
            if header_image:
                filename = secure_filename(header_image.filename)
                storagePath = "uploads/" + str(session["user_id"]) + "/"+ filename
                image_link = uploadImageFirebase(header_image,storagePath)
                #header_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                image_link = backupimage
            category = request.form['category']
            tags = request.form['tags']
            content = request.form['content-news']
            print(title,category,content,image_link,tags,id)
            query = "UPDATE news SET title = %s , content = %s , image = %s , category = %s, tags = %s WHERE id = " + str(id) + " AND published_by = " + str(session['user_id'])+ ""
            data = (title,content,image_link,category,tags)
            with database.cursor() as cursor:
                cursor.execute(query,data)
                database.commit()
        except Exception as e:
            print(e)
    return "Success"
##==========
##TODO: Delete News
##==========
@app.route("/delete-news/<nid>",methods=['GET','POST'])
def deletenews(nid):
    #TODO: session login check not implemented
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    if request.method == 'POST':
        news_id = nid
        query = "DELETE FROM news WHERE id=%s AND published_by = %s"
        data = (news_id,session['user_id'])
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"

##?
##?TODO: Admin Profile & Dashboard Pages END
##?================================================


##?=============================================
##?TODO: Comments CRUD
##?
@app.route("/add-comment",methods=['POST'])
def addComment():
    #TODO: session login check not implemented
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))

    if request.method == 'POST':
        news_id = request.form["news_id"]
        comment = request.form["comment"]
        sentiment = sentiment_scores(comment)
        query = "INSERT INTO comments(post_id, user_id, comment, sentiment) VALUES (%s,%s,%s,%s)"
        data = (news_id,session['user_id'],comment,sentiment)
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
            print(cursor)
            id = cursor.lastrowid
            msg = {
                "id": id,
                "comment" : comment,
                "sentiment" : sentiment,
                "user_img" : session['user_img'],
                "user_name" : session['name'],
            }
            return jsonify(msg)

@app.route("/edit-comment",methods=['POST'])
def editComment():
    #TODO: session login check not implemented
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if request.method == 'POST':
        comment_id = request.form["comment_id"]
        #news_id = request.form["news_id"]
        comment = request.form["comment"]
        sentiment = sentiment_scores(comment)
        query = "UPDATE comments SET comment=%s, sentiment=%s WHERE id = %s"
        data = (comment,sentiment,int(comment_id))
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"
@app.route("/delete-comment",methods=['POST'])
def deleteComment():
    #TODO: session login check not implemented
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if request.method == 'POST':
        comment_id = request.form["comment_id"]
        print(comment_id)
        query = "DELETE FROM comments WHERE id="+ comment_id+  ""
        
        with database.cursor() as cursor:
            cursor.execute(query)
            database.commit()
            return "Success"

def listComments(news_id):
    """
    This function list all the comments using news id and performing the join operation.
    """
    query = """SELECT id,name, comment, sentiment, timestamp 
               FROM comments 
               LEFT JOIN users 
               ON comments.user_id = users.id 
               WHERE post_id = %s"""
    data = (int(news_id))
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query,data)
        db_data = cursor.fetchall()
        comments = []
        for row in db_data:
            single_comment = {}
            single_comment["comment_id"] = row[0]
            single_comment["name"] = row[1]
            single_comment["comment"] = row[2]
            single_comment["sentiment"] = row[3]
            single_comment["timestamp"] = row[4]
            comments.append(single_comment)
            #print(row)
        total_count = len(comments)
    return (comments,total_count)


#? Comments Reports
@app.route('/report-comment',methods=['GET','POST'])
def reportComment():
    #TODO: session login check
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if request.method == 'POST':
        comment_id = request.form["comment_id"]
        query = "UPDATE comments SET reports= ( reports + 1 ) WHERE id=%s"
        data = (int(comment_id))
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"

@app.route('/rm-report-comment',methods=['GET','POST'])
def removeReport():
    #TODO: session login check
    # If not true than redirect
    if not loginCheck():
        return redirect(url_for('login'))
    if request.method == 'POST':
        comment_id = request.form["comment_id"]
        query = "UPDATE comments SET reports= ( reports - 1 ) WHERE id=%s"
        data = (comment_id)
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"

##?
##?TODO: Comments CRUDE END
##?=============================================






##?================================================
##? Misc Pages
##? Newsletter, About, Contact, Privacy policy, Terms&condition, FAQ
##
##* NewsLetter
##
@app.route("/newsletter",methods=['GET','POST'])
def newsletter():
    if request.method == 'POST':
        email = request.form['email']
        #TODO: Send Email
        print(email)
        query = "INSERT INTO newsletter(email) values (%s)"
        data = (email,)
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"
    return "Thanks!"

##
##* About Us
##
@app.route("/about-us")
def aboutus():
    return render_template("aboutus.html")

##
##* FAQ
##
@app.route("/faq")
def faq():
    return render_template("faq.html")

##
##TODO: Contact Us
##
@app.route("/contact-us",methods=['GET','POST'])
def contactus():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        phone = request.form['phoneno']
        message = request.form['message']
        print(name,email,subject,phone,message)
        
        return "Nice, work bubu <3 "
    return render_template("contactus.html")

##
##* Privacy Policy
##
@app.route("/privacy-policy")
def privacypolicy():
    return render_template("terms-and-condition.html")

##
##* Terms & Condition
##
@app.route("/terms-and-condition")
def termsncondition():
    
    return render_template("terms-and-condition.html")
##?
##? Misc Pages END
##?================================================

##!
##! Flask Custom Filters
##!
@app.template_filter()
def url_gen(url):
    """Remove Bad charater and add - where space & trims it"""
    
    trim_url = url.rsplit('/', 1)[-1]
    cleanString = re.sub('\W+','-', trim_url )
    return cleanString.lower()

@app.template_filter()
def news_summarizer(data):
    """Gives summary"""
    
    data = bs4.BeautifulSoup(data,'html.parser')
    news = data.text
    try:
        summary = summarize(news)
    
    except ValueError:
        summary = "This News cant be summarize"
    # print(summary)
    return summary

def loginCheck():
    if 'user_id' not in session:
        return False
    else:
        return True

def isAdminCheck():
    if 'account_type' in session:
        if int(session["account_type"]) != 1:
            return True
        else:
            return False
    else:
        return False

@app.template_filter()      
def classifyNews(news):
    data = bs4.BeautifulSoup(news,'html.parser')
    data = data.text
    prediction = classifier.predict([data])
    print(prediction)
    return prediction[0]

def sendBulkEmail():
    query = "select email from newsletter"
    receivers = []
    with database.cursor(buffered=True) as cursor:
            cursor.execute(query)
            db_data = cursor.fetchall()
            for row in db_data:
                print(row[0])
                receivers.append(row[0])
    #send email from here
    msg = Message('Hello', sender = 'sem6@neeldeshmukh.com', recipients = receivers)
    msg.body = "Hello Flask message sent from Flask-Mail"
    mail.send(msg)

def uploadImageFirebase(image,storagePath):
    file = storage.child(storagePath).put(image)
    url = storage.child(storagePath).get_url(file['downloadTokens'])
    return url
##!
##! Server Error Handler
##!



##*
##* 404 Handler
##*
@app.errorhandler(404) 
def not_found(e): 
  return render_template("404.html")

if __name__ == '__main__':
    app.run(debug=True)
