
from flask import Flask, render_template,  redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,SelectField,FileField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image= db.Column(db.Text)
    quantity=db.Column(db.Integer, default=0)
    reviews = db.relationship('Reviews', back_populates='movie')



class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    grade=db.Column(db.Integer)
    movie_id=db.Column(db.Integer,db.ForeignKey('movie.id'))
    movie = db.relationship('Movie', back_populates='reviews')


db.create_all()

class ReviewForm(FlaskForm):
    author=StringField('Ваше Имя', validators=[DataRequired(message = 'Поле не должно быть пустым')])
    text = TextAreaField('Текст отзыва', validators=[DataRequired(message='Поле не должно быть пустым')])
    grade = SelectField('Оценка',choices=[(i,i) for i in range(1,11)])
    submit = SubmitField('Добавить отзыв')

class MovieForm(FlaskForm):
    title=StringField('Название', validators=[DataRequired(message = 'Поле не должно быть пустым')])
    description = TextAreaField('Описание', validators=[DataRequired(message='Поле не должно быть пустым')])
    image = FileField('Изображение',validators=[FileRequired(message = 'Поле не должно быть пустым'), FileAllowed(['jpg','jpeg','png'],message='Неверный форрмат файла')])
    submit = SubmitField('Добавить фильм')



@app.route('/')
def index():
    movie = Movie.query.all()
    reviews = Reviews.query.all()
    return render_template('index.html',movie=movie,reviews=reviews)


@app.route('/movie/<id>',methods=['GET', 'POST'])
def movie(id):
    movie=Movie.query.get(id)
    reviews=Reviews.query.all()
    form = ReviewForm()
    if movie.quantity==0:
        av=0
    else: av=aver(id)
    if form.validate_on_submit():
        review = Reviews()
        review.author = form.author.data
        review.text = form.text.data
        review.grade = form.grade.data
        movie.quantity+=1
        review.movie_id=id
        db.session.add(review)
        db.session.commit()
        db.session.add(movie)
        db.session.commit()
        return redirect(url_for('movie',movie=movie,reviews=reviews, id=movie.id,av=av))

    return render_template('movie.html',movie=movie,reviews=reviews,form=form, av=av )


@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    form= MovieForm()
    if form.validate_on_submit():
        movie=Movie()
        movie.title=form.title.data
        movie.description=form.description.data
        image=form.image.data
        image_name= secure_filename(image.filename)
        UPLOAD_FOLDER.mkdir(exist_ok=True)
        image.save(UPLOAD_FOLDER/image_name)
        movie.image = image_name
        db.session.add(movie)
        db.session.commit()
        return redirect(url_for('movie', id=movie.id))
    return render_template('add_movie.html',form=form)



@app.route('/reviews/')
def reviews():
    reviews=Reviews.query.order_by(Reviews.created_date.desc()).all()
    return render_template('reviews.html', reviews=reviews)


@app.route('/delete_review/<id>')
def delete_review(id):
    review=Reviews.query.get(id)
    review.movie.quantity-=1
    db.session.delete(review)
    db.session.commit()
    db.session.commit()
    return redirect(url_for('reviews'))

def aver(id):
    reviews=Reviews.query.all()
    movie=Movie.query.get(id)
    c=0
    for review in movie.reviews:
        c+=review.grade
    return round(c/movie.quantity,1)

if __name__ == '__main__':
    app.run(debug=True)
