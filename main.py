from flask import *
import hashlib
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
# create client
ow = openweather.OpenWeather()

app = Flask(__name__,template_folder='templates')
app.secret_key = 'this is a very secure string'
# UPLOAD_FOLDER = 'static/uploads'
# ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(GEOIPIFY_API_KEY='at_v1LEHVAlNSSUFAb6T3ONOJcNdy2WU')
newsapi = NewsApiClient(api_key="18cd6534eefc44db90cb02e7ef2cb9fc")
simple_geoip = SimpleGeoIP(app)

# Email config
app.config['MAIL_SERVER']='smtp.stackmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sem6@neeldeshmukh.com'
app.config['MAIL_PASSWORD'] = 'Gr5d4aa42'
app.config['MAIL_USE_TLS'] = False
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
except Exception as e:
    print(e)




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
    return render_template("news/blog.html")

##==========
##TODO: news-grids
##==========
@app.route('/news-grids')
def newsgrids():
    return render_template("news/blog-grid.html")

##==========
##TODO: news detail page
##==========
@app.route('/dp')
def dp():
    return render_template("news/blog-details.html")

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
            query = 'Select name, email, password, type from users'
            with database.cursor(buffered=True) as cursor:
                cursor.execute(query)
                db_data = cursor.fetchall()
                for row in db_data:
                    #print(row[1],row[2])
                    if row[1] == email and row[2] == password:
                        print(row)
                        session['name'] = row[0]
                        session['email'] = email
                        session['account_type'] = row[3]
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
        try:
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
            msg.body = "OTP: " + OTP
            mail.send(msg)           
        except:            
            err = "some error occured! try again."
        return redirect(url_for('verifyotp'))
        
    return render_template("authentication/register.html")

##==========
##TODO: VerifyOTP
##==========
@app.route('/verify-otp',methods=['GET','POST'])
def verifyotp():
    if request.method == 'POST':
        try:
            user_info = session.get('user_info')
            otp = request.form['OTP']
            if str(otp) == str(user_info['OTP']):
                #global database 
                query = "INSERT INTO users(name, email, password, type) VALUES (%s,%s,%s,%s)"
                data = (user_info["name"], user_info["email"],user_info["password"],user_info["account_type"])
                with database.cursor() as cursor:
                    cursor.execute(query,data)
                    database.commit()
                return redirect(url_for('login'))
        except Exception as e:
            print(e)
            #database.rollback()
    return render_template("authentication/verify.html")

##==========
##TODO: Forgot Password
##==========
@app.route('/forgot-password')
def forgotpassword():
    return render_template("authentication/forgotpassword.html")

##==========
##TODO: ChangePassword
##==========
@app.route('/change-password')
def changepassword():
    return redirect(url_for('login'))

##==========
##TODO: Logout
##==========
@app.route('/logout')
def logout():
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
    return render_template("profile/dashboard-bookmark.html")

##?
##?TODO: User Profile & Dashboard Pages END
##?================================================


##?================================================
##?TODO: Admin Profile & Dashboard Pages END
##? Account, Edit Account, Create News, Edit News, Account Preferences

##==========
##TODO: Admin Account
##==========
@app.route('/admin-account')
def adminaccount():
    return render_template("profile/admin/admin-account.html")

##==========
##TODO: Admin Edit Account
##==========
@app.route('/admin-edit-account')
def admineditaccount():
    return render_template("profile/admin/admin-dashboard-edit-profile.html")

##==========
##TODO: Create Admin - News
##==========
@app.route('/create-news')
def admincreatenews():
    return render_template("profile/admin/admin-dashboard-post-news.html")

##==========
##TODO: Edit Admin - News
##==========
@app.route('/edit-news')
def admineditnews():
    return render_template("profile/admin/admin-dashboard-manage-news.html")

##?
##?TODO: Admin Profile & Dashboard Pages END
##?================================================

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
##* Contact Us
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
