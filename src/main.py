"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# GET route
@app.route('/get_todo', methods=['GET'])
def get_todo():

    # get the todo list
    todo = Todo.query.all()

    # map the results and your list of people  inside of the all_people variable
    todo_list = list(map(lambda x: x.serialize(), todo))

    return jsonify(todo_list), 200

# POST route
@app.route('/add_todo', methods=['POST'])
def add_todo():

    request_body = request.get_json()
    item = Todo(done=request_body["done"], label=request_body["label"])
    db.session.add(item)
    db.session.commit()

    # get the todo list
    todo = Todo.query.all()

    # map the results and your list of people  inside of the all_people variable
    todo_list = list(map(lambda x: x.serialize(), todo))

    return jsonify(todo_list), 200

# DELETE route
@app.route('/delete_todo/<int:idx>', methods=['DELETE'])
def delete_todo(idx):

    item = Todo.query.get(idx)
    if item is None:
        raise APIException('Item not found', status_code=404)
    db.session.delete(item)
    db.session.commit()

    # get the todo list
    todo = Todo.query.all()

    # map the results and your list of people  inside of the all_people variable
    todo_list = list(map(lambda x: x.serialize(), todo))

    return jsonify(todo_list), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
