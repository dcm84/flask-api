from email.policy import default
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import datetime


from flask_migrate import Migrate
DATABASE = "quotes.sqlite"

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class AuthorModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(32), unique=False)
   surname = db.Column(db.String(32), unique=False)
   is_active = db.Column(db.Boolean, unique=False, default=True)
   quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic', cascade="all, delete-orphan")

   def __init__(self, name, surname):
       self.name = name
       self.surname = surname

   def __repr__(self):
        return '<Author id=%r name=%r>' % (self.id, self.name)

   def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class QuoteModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
   text = db.Column(db.String(255), unique=False)
   rating = db.Column(db.Integer, unique=False, default=1)
   created = db.Column(db.DateTime(timezone=True), server_default=func.now())

   def __init__(self, author, text, rating):
       self.author_id = author.id
       self.text = text
       self.rating = rating

   def __repr__(self):
        return '<Quote author_id=%r id=%r>' % (self.author_id, self.id)

   def as_dict(self):
      fields_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
      # форматируем дату
      fields_dict["created"] = datetime.datetime.strftime(fields_dict["created"], '%d.%m.%Y')
      return fields_dict

#авторы
@app.route("/author/<int:id>")
def author_by_id(id):
   author = AuthorModel.query.get(id)
   if author is not None:
      return author.as_dict()
   else:
      return { "error": f"Автор не существует: {id}"}, 404

@app.route("/author")
def authors():
   # модный order by
   avaible_sorts = ['id', 'name', 'surname']
   sort_by = request.args.get('sort_by')
   sort_by = sort_by if sort_by in avaible_sorts else "id"
   
   return [i.as_dict() for i in AuthorModel.query.order_by(getattr(AuthorModel, sort_by)).all()]

@app.route("/author", methods=["POST"])
def create_author():
   author_data = request.json
   if "name" not in author_data or "surname" not in author_data:
      return { "error": f"В запросе нехватает одного из обязательных параметров"}, 400
   
   author = AuthorModel(author_data["name"], author_data["surname"])
   db.session.add(author)
   db.session.commit()
   return author.as_dict(), 201

@app.route("/author/<int:id>", methods=['PUT'])
def edit_author(id):
   #Проверяем, что есть, что редактировать
   author = AuthorModel.query.get(id)
   if author is None:
      return { "error": f"Автор не существует: {id}"}, 404
   
   new_data = request.json
   if "name" in new_data:
      author.name = new_data["name"]
   if "surname" in new_data:
      author.surname = new_data["surname"]

   #апдейтим данные
   db.session.commit()

   return author.as_dict(), 200

@app.route("/author/<int:id>", methods=['DELETE'])
def delete_author(id):
   #Проверяем, что есть, что удалять
   author = AuthorModel.query.get(id)
   if author is None:
      return { "error": f"Автор не существует: {id}"}, 404
   
   #удаляем автора
   db.session.delete(author)
   db.session.commit()

   return f"Автор с id={id} успешно удален.", 200

#цитаты
@app.route("/quotes")
def quote():
   return [i.as_dict() for i in QuoteModel.query.all()]

@app.route("/author/<int:author_id>/quotes/<int:quote_id>")
def quote_by_id(author_id, quote_id):

   author = AuthorModel.query.get(author_id)
   if author is None:
      return { "error": f"Автор не существует: {author_id}"}, 404

   quote = QuoteModel.query.filter_by(id=quote_id, author_id=author_id).first()
   if quote is not None:
      return quote.as_dict()
   else:
      return { "error": f"Неправильный id цитаты: {quote_id}"}, 404

@app.route("/author/<int:author_id>/quotes")
def quote_by_author(author_id):

   author = AuthorModel.query.get(author_id)
   if author is None:
      return { "error": f"Автор не существует: {author_id}"}, 404

   quotes = QuoteModel.query.filter_by(author_id=author_id).all()
   return [i.as_dict() for i in quotes]

@app.route("/author/<int:author_id>/quotes", methods=["POST"])
def create_quote(author_id):
   author = AuthorModel.query.get(author_id)
   if author is None:
      return { "error": f"Автор не существует: {author_id}"}, 404

   new_quote = request.json
   if "text" not in new_quote:
      return { "error": f"В запросе не хватает поля text"}, 400

   q = QuoteModel(author, new_quote["text"], new_quote["rating"] if "rating" in new_quote and new_quote["rating"] > 0 and new_quote["rating"] < 6 else 1)
   db.session.add(q)
   db.session.commit()
   return jsonify(q.as_dict()), 201

@app.route("/author/<int:author_id>/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(author_id, quote_id):
   #Проверяем, что есть, что редактировать
   author = AuthorModel.query.get(author_id)
   if author is None:
      return { "error": f"Автор не существует: {author_id}"}, 404

   quote = QuoteModel.query.filter_by(id=quote_id, author_id=author_id).first()
   if quote is None:
      return { "error": f"Неправильный id цитаты: {quote_id}"}, 404
   
   new_data = request.json
   if "rating" in new_data and new_data["rating"] > 0 and new_data["rating"] < 6:
      quote.rating = new_data["rating"]
   if "text" in new_data:
      quote.text = new_data["text"]

   #апдейтим данные
   db.session.commit()

   return quote.as_dict(), 200

@app.route("/author/<int:author_id>/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(author_id, quote_id):
   #Проверяем, что есть, что удалять
   author = AuthorModel.query.get(author_id)
   if author is None:
      return { "error": f"Автор не существует: {author_id}"}, 404

   quote = QuoteModel.query.filter_by(id=quote_id, author_id=author_id).first()
   if quote is None:
      return { "error": f"Неправильный id цитаты: {quote_id}"}, 404
   
   #удаляем цитату
   db.session.delete(quote)
   db.session.commit()

   return f"Цитата с id={id} успешно удалена.", 200

@app.route("/author/<int:author_id>/quotes/<int:quote_id>/increase_rating", methods=['PUT'])
def increase_quote_rating(author_id, quote_id):
   author = AuthorModel.query.get(author_id)
   if author is None:
      return { "error": f"Автор не существует: {author_id}"}, 404

   quote = QuoteModel.query.filter_by(id=quote_id, author_id=author_id).first()
   if quote is None:
      return { "error": f"Неправильный id цитаты: {quote_id}"}, 404
   
   if quote.rating < 5:
      quote.rating = quote.rating + 1
      db.session.commit()
   
   return quote.as_dict(), 200

@app.route("/author/<int:author_id>/quotes/<int:quote_id>/decrease_rating", methods=['PUT'])
def decrease_quote_rating(author_id, quote_id):
   author = AuthorModel.query.get(author_id)
   if author is None:
      return { "error": f"Автор не существует: {author_id}"}, 404

   quote = QuoteModel.query.filter_by(id=quote_id, author_id=author_id).first()
   if quote is None:
      return { "error": f"Неправильный id цитаты: {quote_id}"}, 404
   
   if quote.rating > 1:
      quote.rating = quote.rating - 1
      db.session.commit()
   
   return quote.as_dict(), 200

if __name__ == "__main__":
   app.run(debug=True)
