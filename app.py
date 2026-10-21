from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Cosmo040517$@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure JWT secret key
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change this to a strong random key in production

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

# ===============================
# Database Models
# ===============================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True)
    orders = db.relationship('Order', backref='user', lazy=True)

order_product = db.Table('order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    products = db.relationship('Product', secondary=order_product, backref='orders')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    price = db.Column(db.Float)

# ===============================
# Marshmallow Schemas
# ===============================

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# ===============================
# Create tables
# ===============================

with app.app_context():
    db.create_all()

# ===============================
# JWT Authentication Endpoints
# ===============================

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    if not email:
        return jsonify({"msg": "Missing email"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Create JWT token valid for 30 minutes
    access_token = create_access_token(identity=email, expires_delta=timedelta(minutes=30))
    return jsonify(access_token=access_token)

# ===============================
# User Endpoints (JWT protected)
# ===============================

@app.route('/users', methods=['POST'])
@jwt_required()
def add_user():
    name = request.json['name']
    address = request.json['address']
    email = request.json['email']
    new_user = User(name=name, address=address, email=email)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    # Pagination: ?page=1&per_page=5
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    users_paginated = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return users_schema.jsonify(users_paginated.items)

@app.route('/users/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.get_or_404(id)
    return user_schema.jsonify(user)

@app.route('/users/<id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    user = User.query.get_or_404(id)
    user.name = request.json['name']
    user.address = request.json['address']
    user.email = request.json['email']
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/users/<id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

# ===============================
# Product Endpoints (pagination example)
# ===============================

@app.route('/products', methods=['POST'])
def add_product():
    product_name = request.json['product_name']
    price = request.json['price']
    new_product = Product(product_name=product_name, price=price)
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product)

@app.route('/products', methods=['GET'])
def get_products():
    # Pagination: ?page=1&per_page=5
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    products_paginated = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    return products_schema.jsonify(products_paginated.items)

@app.route('/products/<id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return product_schema.jsonify(product)

@app.route('/products/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    product.product_name = request.json['product_name']
    product.price = request.json['price']
    db.session.commit()
    return product_schema.jsonify(product)

@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})

# ===============================
# Order Endpoints
# ===============================

@app.route('/orders', methods=['POST'])
def create_order():
    user_id = request.json['user_id']
    order_date = datetime.strptime(request.json['order_date'], "%Y-%m-%d")
    new_order = Order(user_id=user_id, order_date=order_date)
    db.session.add(new_order)
    db.session.commit()
    return order_schema.jsonify(new_order)

@app.route('/orders/<order_id>/add_product/<product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    order = Order.query.get_or_404(order_id)
    product = Product.query.get_or_404(product_id)
    if product not in order.products:
        order.products.append(product)
        db.session.commit()
    return order_schema.jsonify(order)

@app.route('/orders/<order_id>/remove_product/<product_id>', methods=['DELETE'])
def remove_product_from_order(order_id, product_id):
    order = Order.query.get_or_404(order_id)
    product = Product.query.get_or_404(product_id)
    if product in order.products:
        order.products.remove(product)
        db.session.commit()
    return order_schema.jsonify(order)

@app.route('/orders/user/<user_id>', methods=['GET'])
def get_orders_by_user(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    return orders_schema.jsonify(orders)

@app.route('/orders/<order_id>/products', methods=['GET'])
def get_order_products(order_id):
    order = Order.query.get_or_404(order_id)
    return products_schema.jsonify(order.products)

# Advanced bonus: Get total price of an order
@app.route('/orders/<order_id>/total', methods=['GET'])
def get_order_total(order_id):
    order = Order.query.get_or_404(order_id)
    total = sum(product.price for product in order.products)
    return jsonify({'order_id': order_id, 'total_price': total})

# ===============================
# Run the app
# ===============================

if __name__ == '__main__':
    app.run(debug=True)
