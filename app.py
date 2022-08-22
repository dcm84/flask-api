from random import randint
from flask import Flask, request

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

about_me = {
   "name": "Евгений",
   "surname": "Юрченко",
   "email": "eyurchenko@specialist.ru"
}

quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.",
       "rating": 3,
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.",
       "rating": 2,
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.",
       "rating": 5,
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так.",
       "rating": 5,
   },
]

def get_next_quote_id():
   '''
   Возвращает доступный id для новой записи (упорядочены по возрастанию)
   '''
   if len(quotes) < 1:
      return 1
   return quotes[len(quotes) - 1]["id"] + 1

def get_quote_index_by_id(id):
   '''
   Возвращает index Записи по id
   '''
   for index, quote in enumerate(quotes):
      if quote["id"] == id:
         return index

   return None

@app.route("/")
def hello_world():
   return "Hello, World!"

@app.route("/about")
def about():
   return about_me

@app.route("/quotes")
def quote():
   return quotes

@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json
   data["id"] = get_next_quote_id()
   data["rating"] = 1
   quotes.append(data)
   return data, 201

@app.route("/quotes/<int:id>")
def quote_by_id(id):
   quote_index = get_quote_index_by_id(id)
   if quote_index != None:
      return quotes[quote_index]
   else:
      return { "error": f"Неправильный id цитаты: {id}"}, 404

@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
   new_data = request.json
   quote_index = get_quote_index_by_id(id)
   if quote_index == None:
      return { "error": f"Неправильный id цитаты: {id}"}, 404
   
   if "author" in new_data:
      quotes[quote_index]["author"] = new_data["author"]
   if "text" in new_data:
      quotes[quote_index]["text"] = new_data["text"]

   return quotes[quote_index], 200

@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
   quote_index = get_quote_index_by_id(id)
   if quote_index == None:
      return { "error": f"Неправильный id цитаты: {id}"}, 404

   del quotes[quote_index]

   return f"Цитата с id={id} успешно удалена.", 200


@app.route("/quotes/count")
def quotes_count():
   return { "count": len(quotes)}

@app.route("/quotes/random")
def random_quote():
   return quotes[randint(0, len(quotes) - 1)]

@app.route("/quotes/filter")
def filtered_quotes():
   author = request.args.get('author')
   quotes_filtered = quotes[:]

   if author:
      #мягкий поиск
      quotes_filtered = list(filter(lambda s: s["author"].find(author) != -1, quotes_filtered))


   rating = request.args.get('rating')
   if rating:
      quotes_filtered = list(filter(lambda s: s["rating"] == int(rating), quotes_filtered))
   
   return quotes_filtered
   
if __name__ == "__main__":
   app.run(debug=True)
