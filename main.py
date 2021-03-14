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
    geoip_data = simple_geoip.get_geoip_data()
    location = geoip_data['location']
    city = location['city']
    weather_data = get_weather("mumbai")
    print(weather_data)
    headline = ""
    all_headlines = newsapi.get_top_headlines(category="general",
    language='en',country="in")
    news_articles = all_headlines.get('articles')
    for news in news_articles:
        headline += news['title'] + " "
    return render_template("index.html",
                            headlines=headline,
                            location=location,
                            weather_data=weather_data,
                            day=datetime.datetime.today().strftime('%d'),month=datetime.datetime.today().strftime('%h'))

#date article reference : https://stackoverflow.com/questions/28189442/datetime-current-year-and-month-in-python

#
#* Scraper & application object store
#
@app.context_processor
def category_data():
    response_obj = newsapi.get_everything(
                                    language='en',
                                    q='Technology')
    Tech_all_articles = response_obj["articles"]
    response_obj1 = newsapi.get_everything(
                                    language='en',
                                    q='entertainment')
    Entertainment_all_articles = response_obj1["articles"]
    articles = {}
    articles["technology"] = Tech_all_articles
    articles["entertainment"] =Entertainment_all_articles
    return dict(articles = articles)

#
# Blog.html is used here. make other blog page for non scrape articles later
#    
#Tech route
@app.route('/technology')
def techo_articles():
    return render_template("news/blog.html",category='technology')

#entertainment route
@app.route('/entertainment')
def entertain_articles():
    return render_template("news/blog.html",category='entertainment')

@app.route('/article/<category>/<title>',methods=['GET','POST'])
def scrape_article(category,title):
    category = category
    title = title
    return render_template("news/blog-details-scraped.html",category = category, title = title)
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

# from GoogleNews import GoogleNews
# googlenews = GoogleNews()

#
#? Scraped News Category data using google news module  
#
# @app.route('/category/<category_name>',methods=['GET','POST'])
# def category_scrape(category_name):
#     if request.method == 'GET':
#         category_name = category_name
#         if not session[category_name]:
#             response_obj = newsapi.get_everything(
#                                             language='en',
#                                             category=category_name)
#             all_articles = response_obj["articles"]
#             session[category_name] = all_articles

#         else:
#             pass   
#     return "hi"


##==========
##* Web Stories
##==========
@app.route('/web-stories')
def webstories():
    stories = [
    {
        "id":1,
        "head":"Dogs",
        "src" :"/static/assets/dog.jpg",
        "content": "Bubus are very very cute ekdum smol & sexy cuties"
    },
    {
        "id":2,
        "head":"Cats",
        "src" : "/static/assets/bookend_cats.jpg",
        "content": "Hello, cats are very cute, only some of them are, rest trash."
    },
    {
        "id":3,
        "head":"Parrots",
        "src" : "/static/assets/bird.jpg",
        "content": "hehehehheahjahfkjhdfkhadkjfhkjahfkjhajkfhdjkhfjakdhfkjdhfkj i bite u"
    }]
    return render_template("news/stories.html",stories=stories)

##?================================================
##TODO: News Display Pages
##? 

##==========
##TODO: news
##==========
@app.route('/news')
def news():
    #TODO: LIST NEWS recent
    news_list = []
    query = 'SELECT id, title, content, published_date, published_by FROM news ORDER BY timestamp ASC LIMIT 50'
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query)
        db_data = cursor.fetchall()
        for row in db_data:
            #print(row[1],row[2])
            news = {}
            news['id'] = row[0]
            news['title'] = row[1]
            news['content'] = row[2]
            news['date'] = row[3]
            news['author'] = row[4]
            news_list.append(news)
    #PUSH OBJECT in FLASK and Perform pagination
    return render_template("news/blog.html",news=news_list)

##==========
##TODO: news-grids
##==========
# @app.route('/news-grids')
# def newsgrids():
#     return render_template("news/blog-grid.html")

##==========
##TODO: news detail page
##==========
@app.route('/dp/<category>/<slug>')
def dp(category,slug):
    news = {}
    query = 'SELECT id, title, content, published_date, published_by, image, tags, FROM news WHERE slug = %s AND category = %s'
    data = (str(category),str(slug))
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query,data)
        db_data = cursor.fetchall()
        for row in db_data:
            #print(row[1],row[2])
            news['id'] = row[0]
            news['title'] = row[1]
            news['content'] = row[2]
            news['date'] = row[3]
            news['author'] = row[4]
            news['headerimg'] = row[5]
            news['tags'] = row[6]
    #Comment
    comment_list = []
    query = """SELECT comments.id, users.name, comment, sentiment, timestamp  
               FROM comments
               LEFT JOIN users
               ON comments.user_id = users.id
               WHERE post_id = %d"""
    data = (int(1))
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query,data)
        db_data = cursor.fetchall()
        for row in db_data:
            #print(row[1],row[2])
            comment = {}
            comment['id'] = row[0]
            comment['name'] = row[1]
            comment['comment'] = row[2]
            comment['sentiment'] = row[3]
            comment['timestamp'] = row[4]
            comment_list.append(comment)
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
            query = 'Select id, name, email, password, type from users'
            with database.cursor(buffered=True) as cursor:
                cursor.execute(query)
                db_data = cursor.fetchall()
                for row in db_data:
                    #print(row[1],row[2])
                    if row[2] == email and row[3] == password:
                        print(row)
                        session['user_id'] = row[0]
                        session['name'] = row[1]
                        session['email'] = email
                        session['account_type'] = row[4]
                        return redirect(url_for('index'))
                    else:
                        return render_template("authentication/login.html",msg="No data was found")
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
        msg = Message('OTP', sender = 'sem6@neeldeshmukh.com',
                                recipients = [email])
        msg.body = "OTP: " + str(OTP)
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
            query = "INSERT INTO users(name, email, password, type) VALUES (%s,%s,%s,%s)"
            data = (user_info["name"], user_info["email"],user_info["password"],user_info["account_type"])
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

@app.route('/change-fp')
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
    return render_template("forgot-changepass.html")
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

    # List Favourites here
    # user_id = session["user_id"]
    # query = """SELECT favorites.id, title, slug, timestamp 
    #            FROM favorites
    #            LEFT JOIN news on favorites.post_id = news.id
    #            WHERE favorites.user_id = %d
    #         """
    # data = (int(user_id))
    # with database.cursor(buffered=True) as cursor:
    #     cursor.execute(query,data)
    #     db_data = cursor.fetchall()
    #     favourites = []
    #     for row in db_data:
    #         fav = {}
    #         fav["post_id"] = row[0]
    #         fav["title"] = row[1]
    #         fav["slug"] = row[2]
    #         fav["timestamp"] = row[3]
    #         favourites.append(fav)
        
    return render_template("profile/account.html")
##==========
##TODO: Edit Account
##==========
@app.route('/edit-account')
def editaccount():

    return render_template("profile/dashboard-edit-profile.html")

##==========
##TODO: View
##==========
@app.route('/view-bookmarked')
def viewbookmarked():
    #TODO: login Check

    # List Read Later here
    # user_id = session["user_id"]
    # query = """SELECT readlater.id, title, slug, timestamp 
    #            FROM favorites
    #            LEFT JOIN news on readlater.post_id = news.id
    #            WHERE readlater.user_id = %d
    #         """
    # data = (int(user_id))
    # with database.cursor(buffered=True) as cursor:
    #     cursor.execute(query,data)
    #     db_data = cursor.fetchall()
    #     readlaters = []
    #     for row in db_data:
    #         fav = {}
    #         fav["post_id"] = row[0]
    #         fav["title"] = row[1]
    #         fav["slug"] = row[2]
    #         fav["timestamp"] = row[3]
    #         readlaters.append(fav)
    #make sure u copy the template or jinja2 part from favourites to here!
    return render_template("profile/dashboard-bookmark.html")

##==========
##TODO: Add to Favourite
##==========
@app.route('/at-fav',methods=['GET','POST'])
def at_fav():
    #TODO: Login Check Not Added Yet
    news_id = request.args.get('nid')
    # query = "INSERT INTO favorites(post_id, user_id) VALUES (%d,%d)"
    # data = (int(news_id),int(session['user_id']))
    # with database.cursor() as cursor:
    #     cursor.execute(query,data)
    #     database.commit()   
    return jsonify({'msg':'Added To Fav'})
##==========
##TODO: Remove to Favourite
##==========
@app.route('/rm-fav',methods=['GET','POST'])
def rm_fav():
    #TODO: Login Check Not Added Yet
    news_id = request.args.get('nid')
    # query = "DELETE FROM favorites WHERE post_id = %d AND user_id = %d"
    # data = (int(news_id),int(session['user_id']))
    # with database.cursor() as cursor:
    #     cursor.execute(query,data)
    #     database.commit()   
    return jsonify({'msg':'Added To Fav'})

##==========
##TODO: Add to Read Later
##==========
@app.route('/at-rl',methods=['GET','POST'])
def at_rl():
    #TODO: Login Check Not added
    news_id = request.args.get('nid')
    query = "INSERT INTO readlater(post_id, user_id) VALUES (%d,%d)"
    data = (int(news_id),int(session['user_id']))
    with database.cursor() as cursor:
        cursor.execute(query,data)
        database.commit()   
    return flask.Response(status=200)

##==========
##TODO: Remove from Read Later
##==========
@app.route('/rm-rl',methods=['GET','POST'])
def rm_rl():
    #TODO: Login Check Not added
    news_id = request.args.get('nid')
    query = "DELETE FROM readlater WHERE post_id = %d AND user_id = %d"
    data = (int(news_id),int(session['user_id']))
    with database.cursor() as cursor:
        cursor.execute(query,data)
        database.commit()   
    return flask.Response(status=200)



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
    if request.method == 'POST':
        user_id = session["user_id"]
        #check if current password is correct
        password = request.form['password']
        password = hashlib.md5(password.encode()).hexdigest()

        new_pass = request.form['newpassword']
        new_pass = hashlib.md5(new_pass.encode()).hexdigest()

        query = 'SELECT id, password from users WHERE id=%d'
        data = (int(user_id))
        with database.cursor(buffered=True) as cursor:
            cursor.execute(query,data)
            db_data = cursor.fetchall()
            for row in db_data:
                if row[1] == password:
                    #update with the new password
                    update_query = "UPDATE users SET password = %s WHERE id = %d"
                    update_data = (new_pass,int(user_id))
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
    if request.method == 'POST':
        user_id = session["user_id"]
        
        full_name = request.form['name']
        query = 'UPDATE users SET name=%s WHERE id=%d'
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
    if request.method == 'POST':
        user_id = session["user_id"]
        #TODO: check if image exist
        image = request.form['image']
        #TODO: add Image to Firebase and add link in mysql
        query = 'UPDATE users SET image=%s WHERE id=%d'
        download_url = ""
        data = (download_url,int(user_id))
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
    if request.method == 'POST':
        user_id = session["user_id"]
        #check if current password is correct
        password = request.form['password']
        password = hashlib.md5(password.encode()).hexdigest()

        query = 'SELECT id, password from users WHERE id=%d'
        data = (int(user_id))
        with database.cursor(buffered=True) as cursor:
            cursor.execute(query,data)
            db_data = cursor.fetchall()
            for row in db_data:
                if row[1] == password:
                    #update with the new password
                    update_query = "DELETE from users WHERE id = %d"
                    update_data = (int(user_id))
                    with database.cursor(buffered=True) as cursor:
                        cursor.execute(update_query,update_data)
                        database.commit()
                    #return logout and relogin after password change
                    return redirect(url_for('logout'))
    else:
        return "None"

##?================================================
##?TODO: Admin Profile & Dashboard Pages END
##? Account, Edit Account, Create News, Edit News, Account Preferences

##==========
##TODO: Admin Account
##==========
@app.route('/admin-account')
def adminaccount():
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    #TODO: List Published news
    #SORT with date
    query = "SELECT id, title, published_date FROM news WHERE published_by = '%d'"
    data = (int(session['user_id']))
    recent_published_news = []
    news = {}
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query,data)
        db_data = cursor.fetchall()
        for row in db_data:
            news['id'] = row[0]
            news['title'] = row[1]
            news['published_date'] = row[2]
            recent_published_news.append(news)
            news.clear()
    return render_template("profile/admin/admin-account.html")

##==========
##TODO: Admin Edit Account
##==========
@app.route('/admin-edit-account')
def admineditaccount():
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    return render_template("profile/admin/admin-dashboard-edit-profile.html")

##==========
##TODO: Create Admin - News
##==========
@app.route('/create-news',methods=['GET','POST'])
def admincreatenews():
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    if request.method == 'POST':
        image_link = ""
        title = request.form['news-title']
        slug = slug_gen(title)
        #upload this to firebase storage and get url
        header_image = request.files['image']
        #header_image.save(os.path.join('/static/', header_image.filename))
        # open("static/upload/" + secure_filename(header_image.filename),"w+" ).close()
        # header_image.save('static/upload',secure_filename(header_image.filename))
        if header_image:
            filename = secure_filename(header_image.filename)
            header_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # data = storage.child("1/").put(header_image)
        # image_link = storage.child("1/").get_url(data['downloadTokens'])
        category = request.form['category']
        content = request.form['content-news']
        locality = request.form['locality']
        send_bulk = request.form['bulk-email']
        #publish_by = session['user_id'] 
        print(title,slug,category,content,locality,send_bulk)
        #TODO: News Insert
        return "news created"
    
    return render_template("profile/admin/admin-dashboard-post-news.html")

##==========
##TODO: Manage Admin - News
##==========
@app.route('/edit-news')
def admineditnews():
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    #TODO: Just list the news created by this user give options liked edit, delete and read
    query = "SELECT id, title, published_date FROM news where published_by = %d"
    data = (int(session["user_id"]))
    createdby_news_list = []
    news = {}
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query,data)
        db_data = cursor.fetchall()
        for row in db_data:
            news["id"] = row[0]
            news["title"] = row[1]
            news["date"] = row[2]
            createdby_news_list.append(news)
            news.clear()

    return render_template("profile/admin/admin-dashboard-manage-news.html")

##==========
##TODO: Edit Admin DATA - News
##==========
@app.route('/editnews/<id>')
def admineditnewsdata(nid):
    if 'account_type' not in session:
        return redirect(url_for("index"))
    if int(session["account_type"]) != 1:
        return redirect(url_for("index"))
    #TODO: fill the data with news 
    query = "SELECT title, content, image, category, tags FROM news where id = %d"
    data = (int(nid))
    news = {}
    with database.cursor(buffered=True) as cursor:
        cursor.execute(query,data)
        db_data = cursor.fetchall()
        for row in db_data:
            news["title"] = row[0]
            news["content"] = row[1]
            news["image"] = row[2]
            news["category"] = row[3]
            news["tags"] = row[4]
    print("News on edit data:",news)
    #TODO: Take data and UPDATE
    if request.method == 'POST':
        return "True"
    return render_template("profile/admin/admin-dashboard-edit-news.html")
##?
##?TODO: Admin Profile & Dashboard Pages END
##?================================================


##?=============================================
##?TODO: Comments CRUD
##?
@app.route("/add-comment",methods=['POST'])
def addComment():
    #TODO: session login check not implemented
    if request.method == 'POST':
        news_id = request.form["news_id"]
        comment = request.form["comment"]
        sentiment = sentiment_scores(comment)
        query = "INSERT INTO comments(post_id, user_id, comment, sentiment) VALUES (%d,%d,%s,%s)"
        data = (int(news_id),int(session['user_id']),comment,sentiment)
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"

@app.route("/edit-comment",methods=['POST'])
def editComment():
    #TODO: session login check not implemented
    if request.method == 'POST':
        comment_id = request.form["comment_id"]
        #news_id = request.form["news_id"]
        comment = request.form["comment"]
        sentiment = sentiment_scores(comment)
        query = "UPDATE comments SET comment=%s, sentiment=%s WHERE id=%d"
        data = (comment,sentiment,int(comment_id))
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"
@app.route("/delete-comment",methods=['POST'])
def deleteComment():
    #TODO: session login check not implemented
    if request.method == 'POST':
        comment_id = request.form["comment_id"]
        query = "DELETE FROM comments WHERE id=%d"
        data = (int(comment_id))
        with database.cursor() as cursor:
            cursor.execute(query,data)
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
               WHERE post_id = %d"""
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
    if request.method == 'POST':
        comment_id = request.form["comment_id"]
        query = "UPDATE comments SET reports= ( reports + 1 ) WHERE id=%d"
        data = (int(comment_id))
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"

@app.route('/rm-report-comment',methods=['GET','POST'])
def removeReport():
    #TODO: session login check
    if request.method == 'POST':
        comment_id = request.form["comment_id"]
        query = "UPDATE comments SET reports= ( reports - 1 ) WHERE id=%d"
        data = (int(comment_id))
        with database.cursor() as cursor:
            cursor.execute(query,data)
            database.commit()
            return "Success"

##?
##?TODO: Comments CRUDE END
##?=============================================




@app.route('/jd')
def jd():
    return render_template("news/job-details.html")

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
        print(email)
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
    #sendBulkEmail()
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
