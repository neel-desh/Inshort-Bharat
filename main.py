from flask import *
import hashlib, os
from werkzeug.utils import secure_filename
import requests
app = Flask(__name__,template_folder='templates')
app.secret_key = 'this is a very secure string'
# UPLOAD_FOLDER = 'static/uploads'
# ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


##==========
##* Index
##==========
@app.route('/')
def index():
    return render_template("index.html")

##==========
##* Web Stories
##==========
@app.route('/web-stories')
def webstories():
    return render_template("news/stories.html")


##?================================================
##TODO: Authentication Pages
##? Login, Register, VerifyOTP, ForgotPassword, ResetPassword, Logout

##==========
##TODO: Login
##==========
@app.route('/login')
def login():
    return render_template("authentication/login.html")

##==========
##TODO: Register
##==========
@app.route('/register')
def register():
    return render_template("authentication/register.html")

##==========
##TODO: VerifyOTP
##==========
@app.route('/verify-otp')
def verifyotp():
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
##? Misc Pages
##? Newsletter, About, Contact, Privacy policy, Terms&condition, FAQ
##
##* NewsLetter
##
@app.route("/newsletter")
def newsletter():
    return redirect(url_for('index'))

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
@app.route("/contact-us")
def contactus():
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