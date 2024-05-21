#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]), 200

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404
    
    restaurant_dict = restaurant.to_dict()
    restaurant_dict['restaurant_pizzas'] = [
        {
            'id': rp.id,
            'pizza_id': rp.pizza_id,
            'price': rp.price,
            'restaurant_id': rp.restaurant_id,
            'pizza': rp.pizza.to_dict(only=('id', 'name', 'ingredients'))
        }
        for rp in restaurant.restaurant_pizzas
    ]
    return jsonify(restaurant_dict), 200

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas]), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        price = data['price']
        if price < 1 or price > 30:
            return jsonify({"errors": ["validation errors"]}), 400

        restaurant_pizza = RestaurantPizza(
            restaurant_id=data['restaurant_id'],
            pizza_id=data['pizza_id'],
            price=price
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        response_data = restaurant_pizza.to_dict()
        response_data['pizza'] = restaurant_pizza.pizza.to_dict(only=('id', 'name', 'ingredients'))
        response_data['restaurant'] = restaurant_pizza.restaurant.to_dict(only=('id', 'name', 'address'))
        return jsonify(response_data), 201

    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)
