from flask import Flask, jsonify, render_template, request, abort, make_response
from flask_sqlalchemy import SQLAlchemy
import random
from distutils.util import strtobool

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def return_dict(self):
        dictionary = {}
        # return a dictionary of all column data
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

    def update(self, cafe, request_args):
        for key, value in request.args.items():
            if value == '0' or value == '1':
                value = strtobool(value)
            if key not in self.__dict__:
                error_flag = f"Key '{key}' does not exist. Value not updated."
                return error_flag
            else:
                setattr(self, key, value)
        db.session.commit()



        # for key, value in request.args.items():
        #     print(key, value)
        #     # update each key's value
        #     # setattr(self, key, value)
        #     # dont forget to commit!
        #     db.session.commit()






@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random")
def random_cafe():
    rand_num = random.randrange(0, db.session.query(Cafe).count())
    cafe = Cafe.query.get(rand_num)

    cafe_dict = cafe.return_dict()
    return jsonify(cafe_dict)


@app.route("/all")
def all_records():
    all_cafes = Cafe.query.all()

    cafe = {}
    cafes = []
    cafes_dict = {}
    for record in all_cafes:
        cafe = record.return_dict()
        cafes.append(cafe)
    cafes_dict['cafes'] = cafes
    return jsonify(cafes_dict)


@app.route('/search')
def search():
    error = {
        "error": {
            "Not Found": "Sorry, we don't have a cafe at that location."
        }
    }
    searchword = request.args.get('location')
    # if location isn't found return error
    r = Cafe.query.filter_by(location=searchword).first()
    if not r:
        return jsonify(error)
    else:
        return jsonify(r.return_dict())


# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add():
    success_response = {
        "response": {
            "success": "Successfully added the new cafe."
        }
    }

    error = {
        "error": {
            "Not Found": "Sorry, we don't have a cafe at that location."
        }
    }

    new_cafe = Cafe()
    new_cafe.location = request.args.get('location')
    new_cafe.name = request.args.get('name')
    new_cafe.map_url = request.args.get('map_url')
    new_cafe.img_url = request.args.get('img_url')
    new_cafe.seats = request.args.get('seats')
    new_cafe.has_sockets = int(request.args.get('has_sockets'))
    new_cafe.can_take_calls = int(request.args.get('can_take_calls'))
    new_cafe.has_toilet = int(request.args.get('has_toilet'))
    new_cafe.coffee_price = request.args.get('coffee_price')
    new_cafe.has_wifi = int(request.args.get('has_wifi'))
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(success_response)


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=['PUT', 'PATCH'])
def update_price(cafe_id):
    not_found_error = {
        "error": {
            "Not Found": "Sorry, a cafe with that id was not found in the database."
        }
    }

    failed_update = {
        "Error": {
            "Cafe Not Updated": "Make sure all keys exist in db."
        }
    }

    success = {
        "Success": "Your updates have been successfully applied."
    }

    try:
        cafe = Cafe.query.get(cafe_id)
        cafe_json = cafe.return_dict()
    except AttributeError:
        return jsonify(not_found_error), 404
    else:
        # update cafe with key-values from request.args
        update_error = cafe.update(cafe, request.args)
        if update_error:
            print(update_error)
            return jsonify(failed_update), 422
        return jsonify(success)


@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete(cafe_id):
    user_key = request.args['api-key']
    return user_key



















## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
