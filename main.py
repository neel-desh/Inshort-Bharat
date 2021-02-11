from flask import *
import hashlib, os
from werkzeug.utils import secure_filename
import requests
app = Flask(__name__)
app.secret_key = 'this is a very secure string'
# UPLOAD_FOLDER = 'static/uploads'
# ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


##==========
##* Index
##==========
@app.route('/')
def index():
    return render_template("base.html")

##
##* Web Stories
##
@app.route('/web-stories')
def webstories():
    return render_template("news/stories.html")

##?========================
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




if __name__ == '__main__':
    app.run(debug=False)