from flask import Flask, request
from flask import g
import sqlite3

DATABASE = "quotes.sqlite"

#хочется сразу получать словари из sqlite, а не tuple
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        db.row_factory = dict_factory 
        g._database = db
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    # в документации в примере написан ад, всегда делают fetchall ???
    rv = cur.fetchone() if one else cur.fetchall()
    cur.close()
    return rv

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

#корректно закрываем соединение с БД
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/quotes")
def quote():
   return query_db('select * from quotes')

@app.route("/quotes/<int:id>")
def quote_by_id(id):
   quote = query_db('select * from quotes where id = ?',
      [id], one=True)
   if quote is not None:
      return quote
   else:
      return { "error": f"Неправильный id цитаты: {id}"}, 404

@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json
   if "author" not in data or "text" not in data:
      return { "error": f"В запросе нехватает одного из обязательных параметров"}, 400
   
   #вставляем данные
   db = get_db()
   cur = db.cursor()
   cur.execute('insert into quotes (author, text) values (?, ?)', 
      [data["author"], data["text"]])
   quote_id = cur.lastrowid
   cur.close()
   db.commit()

   #получаем цитату, чтобы вернуть в ответ
   quote = query_db('select * from quotes where id = ?', [quote_id], one=True)   
      
   return quote, 201

@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
   #Проверяем, что есть, что редактировать
   quote = query_db('select * from quotes where id = ?',
      [id], one=True)
   if quote is None:
      return { "error": f"Неправильный id цитаты: {id}"}, 404
   
   new_data = request.json
   if "author" in new_data:
      quote["author"] = new_data["author"]
   if "text" in new_data:
      quote["text"] = new_data["text"]

   #апдейтим данные
   db = get_db()
   db.execute('update quotes set author=?, text=? where id=?', 
      [quote["author"], quote["text"], id])
   db.commit()

   #получаем цитату, чтобы вернуть в ответ
   quote = query_db('select * from quotes where id = ?', [id], one=True)   

   return quote, 200

@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
   #Проверяем, что есть, что удалять
   quote = query_db('select * from quotes where id = ?',
      [id], one=True)
   if quote is None:
      return { "error": f"Неправильный id цитаты: {id}"}, 404

   #удаляем цитату
   db = get_db()
   db.execute('delete from quotes where id=?', [id])
   db.commit()
   return f"Цитата с id={id} успешно удалена.", 200
 
if __name__ == "__main__":
   app.run(debug=True)
