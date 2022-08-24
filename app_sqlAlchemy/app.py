from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

DATABASE = "quotes.sqlite"

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class QuoteModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   author = db.Column(db.String(32), unique=False)
   text = db.Column(db.String(255), unique=False)
   rating = db.Column(db.Integer, unique=False)

   def __init__(self, author, text, rating = 1):
       self.author = author
       self.text  = text
       self.rating = rating

   def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

   def __repr__(self):
        return '<Quote %r id=%r>' % (self.author, self.id)

@app.route("/quotes")
def quote():
   return [i.as_dict() for i in QuoteModel.query.all()]

@app.route("/quotes/<int:id>")
def quote_by_id(id):

   quote = QuoteModel.query.get(id)
   if quote is not None:
      return quote.as_dict()
   else:
      return { "error": f"Неправильный id цитаты: {id}"}, 404

@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json
   if "author" not in data or "text" not in data:
      return { "error": f"В запросе нехватает одного из обязательных параметров"}, 400
   
   #вставляем данные
   q = QuoteModel(data["author"], data["text"], data["rating"] if "rating" in data and data["rating"] > 0 and data["rating"] < 6 else 1)
   db.session.add(q)
   db.session.commit()

   return q.as_dict(), 201

@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
   #Проверяем, что есть, что редактировать
   quote = QuoteModel.query.get(id)
   if quote is None:
      return { "error": f"Неправильный id цитаты: {id}"}, 404
   
   new_data = request.json
   if "author" in new_data:
      quote.author = new_data["author"]
   if "text" in new_data:
      quote.text = new_data["text"]

   #апдейтим данные
   db.session.commit()

   return quote.as_dict(), 200

@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
   #Проверяем, что есть, что удалять
   quote = QuoteModel.query.get(id)
   if quote is None:
      return { "error": f"Неправильный id цитаты: {id}"}, 404
   
   #удаляем цитату
   db.session.delete(quote)
   db.session.commit()

   return f"Цитата с id={id} успешно удалена.", 200

@app.route("/quotes/filter")
def filtered_quotes():
   author = request.args.get('author')
   rating = request.args.get('rating')

   query = QuoteModel.query

   if author:
      #мягонький like-фильтр
      query = query.filter(QuoteModel.author.like(f"%{author}%"))

   if rating:
      query = query.filter_by(rating=rating)
   
   return [i.as_dict() for i in query.all()]

if __name__ == "__main__":
   app.run(debug=True)
