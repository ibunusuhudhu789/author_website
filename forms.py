from flask_wtf import FlaskForm
from wtforms import StringField, URLField, IntegerField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class BookForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    image = URLField("Book_cover", validators=[URL()])
    body = CKEditorField("Blurb", validators=[DataRequired()])
    year = StringField("Year", validators=[DataRequired()])
    isbn = StringField("ISBN", validators=[DataRequired()])
    pages = IntegerField("Pages", validators=[DataRequired()])
    publisher = StringField("Publisher", validators=[DataRequired()])
    language = StringField("Language", validators=[DataRequired()])
    book_format = StringField("Format", validators=[DataRequired()])


class Reviews(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    star = StringField("Your Rating", validators=[DataRequired()])
    review = CKEditorField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Publish it")