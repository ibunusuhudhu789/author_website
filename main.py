from functools import wraps
from flask import Flask, render_template, request, url_for, flash, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from flask_ckeditor import CKEditor
from forms import BookForm, Reviews
from sqlalchemy.orm import relationship
import sendgrid
from sendgrid.helpers.mail import Mail
import requests
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:\\Users\\ibunu\\PycharmProjects\\suhudhu_author_website\\instance\\readers.db"
app.secret_key = os.getenv("SECRETKEY")
recaptcha_site_key = os.getenv("RECAPTCHASITEKEY")
recaptcha_secret_key = os.getenv("RECAPTCHASECRETKEY")
db = SQLAlchemy(app)
ckeditor = CKEditor(app)

login_manager = LoginManager()
login_manager.init_app(app)


# creating the user class
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    reviews = relationship("ReviewsTable", back_populates="readers")


# creating the book class
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    isbn = db.Column(db.String, nullable=False)
    publisher = db.Column(db.String, nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String, nullable=False)
    format = db.Column(db.String, nullable=False)
    reviews = relationship("ReviewsTable", back_populates="books")


# creating the comment class
class ReviewsTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.String, nullable=False)
    review = db.Column(db.String, nullable=False)
    reader_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    readers = relationship("Users", back_populates="reviews")
    books = relationship("Books", back_populates="reviews")


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, user_id)


def admins_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        else:
            return f(*args, **kwargs)

    return wrapper


@app.route("/")
def home():
    all_books = Books.query.all()
    return render_template("index.html", all_books=all_books)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        sendmail = sendgrid.SendGridAPIClient(os.getenv("EMAILKEY"))
        try:
            mail = Mail(from_email=os.getenv("FROM"), to_emails=os.getenv("TO"), subject=f"{subject}", plain_text_content=f"The detials are given below.\nName:{name}\nEmail:{email}\nMessage:{message}")
        except Exception as e:
            print(e)
            flash("Error happened on our server. Try again later")
        else:
            sendmail.send(mail)
            flash("The message is sent successfully!!!")
    return render_template("contact.html")


@app.route("/books")
def books():
    all_books = Books.query.all()
    return render_template("books.html", books=all_books)


@app.route("/book_details/<int:book_num>", methods=["GET", "POST"])
def book_details(book_num):
    form = Reviews()
    selected_book = db.session.get(Books, book_num)
    all_reviews = ReviewsTable.query.all()
    if request.method == "POST":
        review = form.review.data
        rating = form.star.data
        new_review = ReviewsTable(review=review, stars=rating, reader_id=current_user.id, book_id=book_num)
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for("book_details", book_num=book_num))
    return render_template("book-detail.html", book=selected_book, form=form, reviews=all_reviews)


@app.route("/add", methods=["GET", "POST"])
@login_required
@admins_only
def add():
    form = BookForm()
    if request.method == "POST":
        title = form.title.data
        subtitle = form.subtitle.data
        img = form.image.data
        body = form.body.data
        year = form.year.data
        publisher = form.publisher.data
        isbn = form.isbn.data
        book_format = form.book_format.data
        language = form.language.data
        pages = form.pages.data
        new_book = Books(book_title=title, subtitle=subtitle, image=img, body=body, year=year, publisher=publisher,
                         isbn=isbn, format=book_format, language=language, pages=pages)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=form)


@app.route("/edit/<int:book_num>", methods=["GET", "POST"])
@admins_only
def edit(book_num):
    book = db.session.get(Books, book_num)
    form = BookForm(
        title=book.book_title, subtitle=book.subtitle, image=book.image, body=book.body, year=book.year,
        publisher=book.publisher, isbn=book.isbn, book_format=book.format, language=book.language, pages=book.pages
    )
    if request.method == "POST":
        book.book_title = form.title.data
        book.subtitle = form.subtitle.data
        book.image = form.image.data
        book.body = form.body.data
        book.year = form.year.data
        book.publisher = form.publisher.data
        book.isbn = form.isbn.data
        book.format = form.book_format.data
        book.language = form.language.data
        book.pages = form.pages.data
        db.session.commit()
        return redirect(url_for("book_details", book_num=book_num))
    return render_template("edit.html", form=form, num=book_num)


@app.route("/delete/<int:book_num>")
@admins_only
def delete(book_num):
    book = db.session.get(Books, book_num)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        response = request.form.get("g-recaptcha-response")
        url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {
            'secret': recaptcha_secret_key,
            'response': response,
            'remoteip': request.remote_addr}
        result = requests.post(url, data=payload).json()
        if result.get('success'):
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            hashed_password = generate_password_hash(password, "pbkdf2:sha256", 30)
            new_user = Users(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
        else:
            return jsonify({'message': 'reCAPTCHA verification failed.'}), 400
    return render_template("register.html", sitekey=recaptcha_site_key)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user_account = Users.query.filter_by(email=email).first()
        if user_account is not None:
            user_password = user_account.password
            check_password = check_password_hash(user_password, password)
            if check_password:
                login_user(user_account)
                return redirect(url_for("home"))
            else:
                flash("Incorrect password! Try again.")
        else:
            flash("The user is not exists. Try register it or check your email once again.")
    return render_template("login.html")


@app.route("/subscribers", methods=["POST"])
def subscribers():
    email = request.form["subscribers"]
    print(email)
    params = {
        "email": email
    }

    headers = {
        "Authorization": os.getenv("APIKEY"),
        "Content-Type": "application/json"
    }
    try:
        response = requests.post("https://connect.mailerlite.com/api/subscribers", json=params, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(e)
        flash("There is the problem in our server side. Sorry for the problem.")
        return redirect(url_for('home'))
    else:
        flash("You're subscribed to the newsletter!!!")
        return redirect(url_for('home'))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
